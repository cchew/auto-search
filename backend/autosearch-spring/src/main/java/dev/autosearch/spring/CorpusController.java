package dev.autosearch.spring;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import dev.autosearch.CorpusLoader;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/corpus")
public class CorpusController {

    private final PathGuard pathGuard;
    private final ObjectMapper mapper = new ObjectMapper();

    public CorpusController(PathGuard pathGuard) {
        this.pathGuard = pathGuard;
    }

    @GetMapping(produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<List<Map<String, Object>>> corpus() throws IOException {
        return ResponseEntity.ok(CorpusLoader.load(pathGuard.getCorpusPath().toString()));
    }

    @GetMapping(path = "/ui-config", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<Map<String, Object>> uiConfig() throws IOException {
        Map<String, Object> ui = mapper.readValue(
            pathGuard.getUiConfigPath().toFile(), new TypeReference<>() {});
        return ResponseEntity.ok(ui);
    }
}
