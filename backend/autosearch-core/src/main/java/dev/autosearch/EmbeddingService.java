package dev.autosearch;

import ai.djl.huggingface.tokenizers.Encoding;
import ai.djl.huggingface.tokenizers.HuggingFaceTokenizer;
import ai.onnxruntime.OnnxTensor;
import ai.onnxruntime.OrtEnvironment;
import ai.onnxruntime.OrtException;
import ai.onnxruntime.OrtSession;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Path;
import java.util.Map;

public class EmbeddingService implements AutoCloseable {

    private static final Logger log = LoggerFactory.getLogger(EmbeddingService.class);

    private final OrtEnvironment env;
    private final OrtSession session;
    private final HuggingFaceTokenizer tokenizer;

    public EmbeddingService(String modelPath, String tokenizerPath) throws OrtException, IOException {
        log.info("Loading ONNX model from {}", modelPath);
        this.env = OrtEnvironment.getEnvironment();
        this.session = env.createSession(modelPath, new OrtSession.SessionOptions());
        this.tokenizer = HuggingFaceTokenizer.newInstance(Path.of(tokenizerPath));
        log.info("EmbeddingService ready");
    }

    public float[] embed(String text) throws OrtException {
        Encoding enc = tokenizer.encode(text, true, true);
        long[] ids = enc.getIds();
        long[] mask = enc.getAttentionMask();
        long[] types = enc.getTypeIds();
        try (
            OnnxTensor idsTensor   = OnnxTensor.createTensor(env, new long[][]{ids});
            OnnxTensor maskTensor  = OnnxTensor.createTensor(env, new long[][]{mask});
            OnnxTensor typesTensor = OnnxTensor.createTensor(env, new long[][]{types});
            OrtSession.Result result = session.run(Map.of(
                "input_ids",      idsTensor,
                "attention_mask", maskTensor,
                "token_type_ids", typesTensor
            ))
        ) {
            float[][][] hidden = (float[][][]) result.get("last_hidden_state").get().getValue();
            return meanPoolAndNormalize(hidden[0], mask);
        }
    }

    static float[] meanPoolAndNormalize(float[][] tokenEmbeddings, long[] attentionMask) {
        int dim = tokenEmbeddings[0].length;
        float[] pooled = new float[dim];
        float maskSum = 0.0f;
        for (int t = 0; t < tokenEmbeddings.length; t++) {
            float m = attentionMask[t];
            maskSum += m;
            for (int d = 0; d < dim; d++) pooled[d] += tokenEmbeddings[t][d] * m;
        }
        for (int d = 0; d < dim; d++) pooled[d] /= Math.max(maskSum, 1e-9f);
        float norm = 0.0f;
        for (float v : pooled) norm += v * v;
        norm = (float) Math.sqrt(norm);
        if (norm > 1e-9f) for (int d = 0; d < dim; d++) pooled[d] /= norm;
        return pooled;
    }

    @Override
    public void close() throws Exception {
        session.close();
        tokenizer.close();
    }
}
