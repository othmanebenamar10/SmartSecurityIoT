namespace SmartSecurityIoT.Services.Interfaces;

public interface IBiometricService
{
    Task<float[]> GenerateEmbeddingAsync(byte[] imageBytes);
    double CalculateDistance(float[] embedding1, float[] embedding2);
    bool ValidateThreshold(double distance);
    Task<bool> DetectLivenessAsync(byte[] frame);
}
