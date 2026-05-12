package dev.autosearch;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(SearchController.class)
class SearchControllerTest {

    @Autowired MockMvc mvc;
    @Autowired ObjectMapper mapper;
    @MockBean EmbeddingService embeddingService;
    @MockBean SimilarityService similarityService;

    @Test
    void postSearch_returnsMatchingResult() throws Exception {
        float[] vec = new float[384];
        when(embeddingService.embed("GP FTE")).thenReturn(vec);
        when(similarityService.search(vec, 5)).thenReturn(
            List.of(new SearchResult(1, 1, "GP FTE", 0.92f)));

        mvc.perform(post("/api/v1/search")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                        {"query":"GP FTE","topK":5}
                        """))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].itemId").value(1))
            .andExpect(jsonPath("$[0].itemName").value("GP FTE"))
            .andExpect(jsonPath("$[0].score").value(0.92f));
    }

    @Test
    void postSearch_returnsEmptyArrayWhenNoResultsAboveThreshold() throws Exception {
        when(embeddingService.embed(any())).thenReturn(new float[384]);
        when(similarityService.search(any(), anyInt())).thenReturn(List.of());

        mvc.perform(post("/api/v1/search")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                        {"query":"xyzzy","topK":5}
                        """))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$").isEmpty());
    }

    @Test
    void postSearch_returns500OnEmbeddingError() throws Exception {
        when(embeddingService.embed(any())).thenThrow(new RuntimeException("ONNX failure"));

        mvc.perform(post("/api/v1/search")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                        {"query":"test","topK":5}
                        """))
            .andExpect(status().isInternalServerError());
    }

    @Test
    void getHealth_returnsUp() throws Exception {
        mvc.perform(get("/api/v1/search/health"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("UP"));
    }
}
