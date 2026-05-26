using Serilog;
using SmartSecurityIoT.Services.Interfaces;

namespace SmartSecurityIoT.Services;

public class BiometricService : IBiometricService
{
    private const double STRICT_THRESHOLD = 0.40;
    private readonly ILogger _logger = Log.ForContext<BiometricService>();

    public async Task<float[]> GenerateEmbeddingAsync(byte[] imageBytes)
    {
        _logger.Information("Generating face embedding from {Size} bytes", imageBytes.Length);
        await Task.Delay(10);

        // TODO: Utiliser FaceRecognitionDotNet pour générer
        // un embedding 128D depuis le visage détecté.
        return new float[128];
    }

    public double CalculateDistance(float[] embedding1, float[] embedding2)
    {
        double sum = 0;

        for (int i = 0; i < embedding1.Length; i++)
        {
            double diff = embedding1[i] - embedding2[i];
            sum += diff * diff;
        }

        var distance = Math.Sqrt(sum);
        _logger.Debug("Embedding distance: {Distance:F4}", distance);
        return distance;
    }

    public bool ValidateThreshold(double distance)
    {
        bool isMatch = distance <= STRICT_THRESHOLD;
        _logger.Information("Threshold validation: distance={Distance:F4}, threshold={Threshold}, match={IsMatch}",
            distance, STRICT_THRESHOLD, isMatch);
        return isMatch;
    }

    public async Task<bool> DetectLivenessAsync(byte[] frame)
    {
        _logger.Information("Running liveness detection on {Size} bytes", frame.Length);
        await Task.Delay(10);

        // TODO: Implémenter détection clignement yeux,
        // analyse micro mouvements, vérification landmarks.
        return true;
    }
}
