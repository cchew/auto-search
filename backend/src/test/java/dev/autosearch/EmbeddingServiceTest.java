package dev.autosearch;

import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;

class EmbeddingServiceTest {

    @Test
    void meanPoolAndNormalize_producesUnitVector() {
        float[][] tokens = {{3.0f, 0.0f, 0.0f, 0.0f}, {0.0f, 4.0f, 0.0f, 0.0f}};
        long[] mask = {1, 1};
        float[] result = EmbeddingService.meanPoolAndNormalize(tokens, mask);
        float norm = 0;
        for (float v : result) norm += v * v;
        assertThat(Math.sqrt(norm)).isCloseTo(1.0, within(1e-5));
    }

    @Test
    void meanPoolAndNormalize_maskedTokenIgnored() {
        float[][] tokens = {{1.0f, 0.0f}, {999.0f, 999.0f}};
        long[] mask = {1, 0};
        float[] result = EmbeddingService.meanPoolAndNormalize(tokens, mask);
        assertThat(result[0]).isCloseTo(1.0f, within(1e-5f));
        assertThat(result[1]).isCloseTo(0.0f, within(1e-5f));
    }

    @Test
    void meanPoolAndNormalize_averagesActiveTokens() {
        float[][] tokens = {{2.0f, 0.0f}, {4.0f, 0.0f}};
        long[] mask = {1, 1};
        float[] result = EmbeddingService.meanPoolAndNormalize(tokens, mask);
        // mean = [3, 0], normalized = [1, 0]
        assertThat(result[0]).isCloseTo(1.0f, within(1e-5f));
        assertThat(result[1]).isCloseTo(0.0f, within(1e-5f));
    }

    @Test
    void meanPoolAndNormalize_allMasked_returnsZeroVector() {
        float[][] tokens = {{1.0f, 0.0f}, {0.0f, 1.0f}};
        long[] mask = {0, 0};
        float[] result = EmbeddingService.meanPoolAndNormalize(tokens, mask);
        assertThat(result[0]).isCloseTo(0.0f, within(1e-5f));
        assertThat(result[1]).isCloseTo(0.0f, within(1e-5f));
    }
}
