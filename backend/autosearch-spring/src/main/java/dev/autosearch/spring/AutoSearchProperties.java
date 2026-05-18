package dev.autosearch.spring;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "autosearch")
public class AutoSearchProperties {
    private String configPath = "config.yaml";
    private String modelPath;
    private String tokenizerPath;
    private String embeddingsPath;

    public String getConfigPath() { return configPath; }
    public void setConfigPath(String v) { this.configPath = v; }
    public String getModelPath() { return modelPath; }
    public void setModelPath(String v) { this.modelPath = v; }
    public String getTokenizerPath() { return tokenizerPath; }
    public void setTokenizerPath(String v) { this.tokenizerPath = v; }
    public String getEmbeddingsPath() { return embeddingsPath; }
    public void setEmbeddingsPath(String v) { this.embeddingsPath = v; }
}
