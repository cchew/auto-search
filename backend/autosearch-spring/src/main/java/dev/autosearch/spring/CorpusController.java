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
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/corpus")
public class CorpusController {

    private final AutoSearchProperties props;
    private final ObjectMapper mapper = new ObjectMapper();

    public CorpusController(AutoSearchProperties props) {
        this.props = props;
    }

    @GetMapping(produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<List<Map<String, Object>>> corpus() throws IOException {
        return ResponseEntity.ok(CorpusLoader.load(props.getCorpusPath()));
    }

    @GetMapping(path = "/ui-config", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<Map<String, Object>> uiConfig() throws IOException {
        Map<String, Object> ui = mapper.readValue(
            Path.of(props.getUiConfigPath()).toFile(), new TypeReference<>() {});
        return ResponseEntity.ok(ui);
    }
}
