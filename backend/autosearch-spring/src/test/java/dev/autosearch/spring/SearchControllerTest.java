package dev.autosearch.spring;

import dev.autosearch.EmbeddingService;
import dev.autosearch.SearchResult;
import dev.autosearch.SimilarityService;
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
    @MockBean EmbeddingService embeddingService;
    @MockBean SimilarityService similarityService;

    @Test
    void search_returnsResults() throws Exception {
        float[] vec = new float[]{0.1f, 0.2f};
        when(embeddingService.embed("reset password")).thenReturn(vec);
        when(similarityService.search(eq(vec), anyInt()))
            .thenReturn(List.of(new SearchResult(1, 1, "Password Reset", 0.92f)));

        mvc.perform(post("/api/v1/search")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"query":"reset password","topK":5}
                    """))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].itemName").value("Password Reset"))
            .andExpect(jsonPath("$[0].groupId").value(1));
    }

    @Test
    void health_returnsUp() throws Exception {
        mvc.perform(get("/api/v1/search/health"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("UP"));
    }
}
