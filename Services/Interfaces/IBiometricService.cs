<<<<<<< HEAD
using System.Threading.Tasks;

namespace SmartSecurityIoT.Services.Interfaces
{
    public interface IBiometricService
    {
        Task<float[]> GenerateEmbeddingAsync(byte[] image);
        Task<bool> DetectLivenessAsync(byte[] image);
    }
}
=======

namespace SmartSecurityIoT.Services.Interfaces;

public interface IBiometricService
{
    Task<float[]> GenerateEmbeddingAsync(byte[] imageBytes);
    double CalculateDistance(float[] embedding1, float[] embedding2);
    bool ValidateThreshold(double distance);
    Task<bool> DetectLivenessAsync(byte[] frame);
}
>>>>>>> 1040ed1220214f4df9d7b4c004650f5c501a03e8
