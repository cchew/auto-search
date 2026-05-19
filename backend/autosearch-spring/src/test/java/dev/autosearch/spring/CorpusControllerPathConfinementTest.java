package dev.autosearch.spring;

import dev.autosearch.AutoSearchConfig;
import dev.autosearch.EmbeddingService;
import dev.autosearch.SimilarityService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.boot.autoconfigure.AutoConfigurations;
import org.springframework.boot.test.context.runner.ApplicationContextRunner;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;

/**
 * Verifies that PathGuard rejects corpus-path / ui-config-path values that
 * escape the allowed root, and accepts values that are within it.
 *
 * Uses ApplicationContextRunner — no HTTP port is bound, tests are fast.
 * AutoSearchAutoConfiguration is loaded; the heavy beans (EmbeddingService,
 * SimilarityService, AutoSearchConfig) are supplied as mocks so the ONNX
 * model files don't need to exist.
 */
class CorpusControllerPathConfinementTest {

    /**
     * Base runner: loads the autoconfiguration and stubs out the three beans
     * that require model artefacts on disk.
     */
    private final ApplicationContextRunner runner = new ApplicationContextRunner()
            .withConfiguration(AutoConfigurations.of(AutoSearchAutoConfiguration.class))
            .withBean(AutoSearchConfig.class,   () -> mock(AutoSearchConfig.class))
            .withBean(EmbeddingService.class,   () -> mock(EmbeddingService.class))
            .withBean(SimilarityService.class,  () -> mock(SimilarityService.class));

    // -----------------------------------------------------------------------
    // Failing cases: path escapes the allowed root
    // -----------------------------------------------------------------------

    @Test
    void context_fails_when_corpus_path_escapes_allowed_root(@TempDir Path allowedRoot,
                                                              @TempDir Path outsideDir) throws IOException {
        Path outsideCorpus = outsideDir.resolve("corpus.json");
        Files.writeString(outsideCorpus, "[]");

        Path insideUiConfig = allowedRoot.resolve("corpus-ui.json");
        Files.writeString(insideUiConfig, "{}");

        runner.withPropertyValues(
                        "autosearch.allowed-root=" + allowedRoot.toAbsolutePath(),
                        "autosearch.corpus-path=" + outsideCorpus.toAbsolutePath(),
                        "autosearch.ui-config-path=" + insideUiConfig.toAbsolutePath())
                .run(ctx -> assertThat(ctx)
                        .hasFailed()
                        .getFailure()
                        .rootCause()
                        .isInstanceOf(IllegalStateException.class)
                        .hasMessageContaining("corpus-path"));
    }

    @Test
    void context_fails_when_ui_config_path_escapes_allowed_root(@TempDir Path allowedRoot,
                                                                 @TempDir Path outsideDir) throws IOException {
        Path insideCorpus = allowedRoot.resolve("corpus.json");
        Files.writeString(insideCorpus, "[]");

        Path outsideUiConfig = outsideDir.resolve("corpus-ui.json");
        Files.writeString(outsideUiConfig, "{}");

        runner.withPropertyValues(
                        "autosearch.allowed-root=" + allowedRoot.toAbsolutePath(),
                        "autosearch.corpus-path=" + insideCorpus.toAbsolutePath(),
                        "autosearch.ui-config-path=" + outsideUiConfig.toAbsolutePath())
                .run(ctx -> assertThat(ctx)
                        .hasFailed()
                        .getFailure()
                        .rootCause()
                        .isInstanceOf(IllegalStateException.class)
                        .hasMessageContaining("ui-config-path"));
    }

    /**
     * Classic path-traversal: the string contains ".." components that resolve
     * outside the allowed root even though the raw value superficially starts
     * inside it.
     */
    @Test
    void context_fails_on_path_traversal_via_dotdot(@TempDir Path allowedRoot,
                                                     @TempDir Path outsideDir) throws IOException {
        Path outsideCorpus = outsideDir.resolve("traversal-target.json");
        Files.writeString(outsideCorpus, "[]");

        // Construct: allowedRoot/../<outsideDirName>/traversal-target.json
        String traversal = allowedRoot.toAbsolutePath()
                + "/../" + outsideDir.getFileName() + "/traversal-target.json";

        Path insideUiConfig = allowedRoot.resolve("corpus-ui.json");
        Files.writeString(insideUiConfig, "{}");

        runner.withPropertyValues(
                        "autosearch.allowed-root=" + allowedRoot.toAbsolutePath(),
                        "autosearch.corpus-path=" + traversal,
                        "autosearch.ui-config-path=" + insideUiConfig.toAbsolutePath())
                .run(ctx -> assertThat(ctx)
                        .hasFailed()
                        .getFailure()
                        .rootCause()
                        .isInstanceOf(IllegalStateException.class)
                        .hasMessageContaining("corpus-path"));
    }

    // -----------------------------------------------------------------------
    // Passing case: both paths are within the allowed root
    // -----------------------------------------------------------------------

    @Test
    void context_starts_when_both_paths_are_within_allowed_root(@TempDir Path allowedRoot) throws IOException {
        Path corpus = allowedRoot.resolve("corpus.json");
        Files.writeString(corpus, "[]");

        Path uiConfig = allowedRoot.resolve("corpus-ui.json");
        Files.writeString(uiConfig, "{}");

        runner.withPropertyValues(
                        "autosearch.allowed-root=" + allowedRoot.toAbsolutePath(),
                        "autosearch.corpus-path=" + corpus.toAbsolutePath(),
                        "autosearch.ui-config-path=" + uiConfig.toAbsolutePath())
                .run(ctx -> {
                    assertThat(ctx).hasNotFailed();
                    assertThat(ctx).hasSingleBean(PathGuard.class);
                    PathGuard guard = ctx.getBean(PathGuard.class);
                    assertThat(guard.getCorpusPath()).isEqualTo(corpus.toRealPath());
                    assertThat(guard.getUiConfigPath()).isEqualTo(uiConfig.toRealPath());
                });
    }
}
