
using SmartSecurityIoT.Services.Interfaces;

namespace SmartSecurityIoT.Services;

public class BiometricService : IBiometricService
{
    private const double STRICT_THRESHOLD = 0.40;

    public async Task<float[]> GenerateEmbeddingAsync(byte[] imageBytes)
    {
        await Task.Delay(10);

        // TODO:
        // Utiliser FaceRecognitionDotNet pour générer
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

        return Math.Sqrt(sum);
    }

    public bool ValidateThreshold(double distance)
    {
        return distance <= STRICT_THRESHOLD;
    }

    public async Task<bool> DetectLivenessAsync(byte[] frame)
    {
        await Task.Delay(10);

        // TODO:
        // Implémenter :
        // - Détection clignement yeux
        // - Analyse micro mouvements
        // - Vérification landmarks

        return true;
    }
}
