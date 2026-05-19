package dev.autosearch.spring;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "autosearch")
public class AutoSearchProperties {
    private String configPath = "config.yaml";
    private String modelPath;
    private String tokenizerPath;
    private String embeddingsPath;
    private String corpusPath;
    private String uiConfigPath;
    /** Optional. Canonical root that corpus-path and ui-config-path must reside under.
     *  Defaults to the JVM working directory when not set. */
    private String allowedRoot;

    public String getConfigPath() { return configPath; }
    public void setConfigPath(String v) { this.configPath = v; }
    public String getModelPath() { return modelPath; }
    public void setModelPath(String v) { this.modelPath = v; }
    public String getTokenizerPath() { return tokenizerPath; }
    public void setTokenizerPath(String v) { this.tokenizerPath = v; }
    public String getEmbeddingsPath() { return embeddingsPath; }
    public void setEmbeddingsPath(String v) { this.embeddingsPath = v; }
    public String getCorpusPath() { return corpusPath; }
    public void setCorpusPath(String v) { this.corpusPath = v; }
    public String getUiConfigPath() { return uiConfigPath; }
    public void setUiConfigPath(String v) { this.uiConfigPath = v; }
    public String getAllowedRoot() { return allowedRoot; }
    public void setAllowedRoot(String v) { this.allowedRoot = v; }
}
