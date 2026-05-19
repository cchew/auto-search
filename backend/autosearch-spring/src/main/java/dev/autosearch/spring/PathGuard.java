package dev.autosearch.spring;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Startup-time path confinement guard.
 *
 * Resolves corpus-path and ui-config-path to their canonical absolute forms and
 * asserts that both reside under autosearch.allowed-root (defaulting to the JVM
 * working directory when not set). The Spring context fails to start if either
 * path escapes the allowed root.
 *
 * Canonical resolution via Path.toRealPath() (file exists) or
 * toAbsolutePath().normalize() (file does not yet exist) neutralises both ".."
 * traversal sequences and symlink chains that would otherwise escape the root.
 *
 * The resolved paths are cached here and consumed by CorpusController, so the
 * per-request path building in the controller is also eliminated.
 *
 * Declared as a bean via AutoSearchAutoConfiguration — do not annotate with
 * @Component; the autoconfiguration manages its lifecycle.
 */
public class PathGuard {

    private static final Logger log = LoggerFactory.getLogger(PathGuard.class);

    private final Path corpusPath;
    private final Path uiConfigPath;

    public PathGuard(AutoSearchProperties props) {
        Path root = resolveRoot(props.getAllowedRoot());

        this.corpusPath   = resolveAndConfine("corpus-path",    props.getCorpusPath(),    root);
        this.uiConfigPath = resolveAndConfine("ui-config-path", props.getUiConfigPath(),  root);

        log.info("PathGuard: allowed-root   = {}", root);
        log.info("PathGuard: corpus-path    = {}", corpusPath);
        log.info("PathGuard: ui-config-path = {}", uiConfigPath);
    }

    public Path getCorpusPath()   { return corpusPath; }
    public Path getUiConfigPath() { return uiConfigPath; }

    // -------------------------------------------------------------------------

    private static Path resolveRoot(String allowedRoot) {
        try {
            if (allowedRoot != null && !allowedRoot.isBlank()) {
                return Paths.get(allowedRoot).toRealPath();
            }
            return Paths.get(".").toRealPath();
        } catch (IOException e) {
            throw new IllegalStateException(
                    "autosearch.allowed-root cannot be resolved: " + e.getMessage(), e);
        }
    }

    private static Path resolveAndConfine(String propertyName, String rawValue, Path root) {
        if (rawValue == null || rawValue.isBlank()) {
            throw new IllegalStateException(
                    "autosearch." + propertyName + " must not be empty");
        }

        Path candidate;
        try {
            Path p = Paths.get(rawValue);
            // toRealPath() resolves symlinks and ".." — requires the path to exist.
            // Fall back to normalize() (still collapses "..") for not-yet-created paths.
            if (p.toFile().exists()) {
                candidate = p.toRealPath();
            } else {
                candidate = p.toAbsolutePath().normalize();
            }
        } catch (IOException e) {
            throw new IllegalStateException(
                    "autosearch." + propertyName + " cannot be resolved: " + e.getMessage(), e);
        }

        if (!candidate.startsWith(root)) {
            throw new IllegalStateException(
                    "autosearch." + propertyName + " (" + candidate + ") is not within the allowed root ("
                    + root + "). Set autosearch.allowed-root to a parent of this path or move the file.");
        }

        return candidate;
    }
}
