using SmartSecurityIoT.Models;

namespace SmartSecurityIoT.Services.Interfaces;

public interface IDatabaseService
{
    Task InitializeAsync();
    Task<int> AddUserAsync(User user);
    Task<IEnumerable<User>> GetAllUsersAsync();
    Task<User?> GetUserByIdAsync(int id);
    Task DeleteUserAsync(int id);
    Task<int> LogIntrusionEventAsync(IntrusionEvent intrusionEvent);
    Task<IEnumerable<IntrusionEvent>> GetRecentIntrusionEventsAsync(int count = 20);
}
