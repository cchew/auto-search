package dev.autosearch.spring;

import dev.autosearch.AutoSearchConfig;
import dev.autosearch.EmbeddingService;
import dev.autosearch.SimilarityService;
import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;

import java.nio.file.Path;

@AutoConfiguration
@EnableConfigurationProperties(AutoSearchProperties.class)
public class AutoSearchAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public AutoSearchConfig autoSearchConfig(AutoSearchProperties props) throws Exception {
        return AutoSearchConfig.fromYaml(Path.of(props.getConfigPath()));
    }

    @Bean
    @ConditionalOnMissingBean
    public EmbeddingService embeddingService(AutoSearchProperties props) throws Exception {
        return new EmbeddingService(props.getModelPath(), props.getTokenizerPath());
    }

    @Bean
    @ConditionalOnMissingBean
    public SimilarityService similarityService(AutoSearchProperties props, AutoSearchConfig cfg) throws Exception {
        return new SimilarityService(props.getEmbeddingsPath(), cfg);
    }
}
