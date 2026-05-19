package dev.autosearch.spring;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(CorpusController.class)
class CorpusControllerTest {

    static final Path CORPUS_PATH    = Path.of("target/test-corpus/corpus.json");
    static final Path UI_CONFIG_PATH = Path.of("target/test-corpus/corpus-ui.json");

    @Autowired MockMvc mvc;

    @MockBean PathGuard pathGuard;

    @BeforeAll
    static void writeFixtures() throws IOException {
        Path dir = Path.of("target/test-corpus");
        Files.createDirectories(dir);
        Files.writeString(CORPUS_PATH,
            "[{\"service_id\":1,\"category_id\":1,\"title\":\"Password Reset\"}]");
        Files.writeString(UI_CONFIG_PATH,
            "{\"appTitle\":\"IT Service Catalogue\",\"appLede\":\"Search.\"," +
            "\"suggestions\":[],\"groupNames\":{}}");
    }

    @Test
    void get_corpus_returns_items() throws Exception {
        when(pathGuard.getCorpusPath()).thenReturn(CORPUS_PATH.toAbsolutePath());

        mvc.perform(get("/api/v1/corpus"))
           .andExpect(status().isOk())
           .andExpect(jsonPath("$[0].title").value("Password Reset"));
    }

    @Test
    void get_ui_config_returns_labels() throws Exception {
        when(pathGuard.getUiConfigPath()).thenReturn(UI_CONFIG_PATH.toAbsolutePath());

        mvc.perform(get("/api/v1/corpus/ui-config"))
           .andExpect(status().isOk())
           .andExpect(jsonPath("$.appTitle").value("IT Service Catalogue"));
    }
}
