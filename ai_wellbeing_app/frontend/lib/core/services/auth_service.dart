import 'package:shared_preferences/shared_preferences.dart';
import 'package:local_auth/local_auth.dart';
import 'api_client.dart';

class AuthService {
  static const String _pinKey = "history_privacy_pin_hash";
  static const String _biometricEnabledKey = "history_biometric_enabled";
  
  final LocalAuthentication _localAuth = LocalAuthentication();
  final ApiClient _apiClient = ApiClient();

  Future<bool> hasPinSet() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.containsKey(_pinKey);
  }

  Future<void> setPin(String pin) async {
    final hashed = await _apiClient.hashPin(pin);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_pinKey, hashed);
  }

  Future<bool> verifyPin(String pin) async {
    final prefs = await SharedPreferences.getInstance();
    final storedHash = prefs.getString(_pinKey);
    if (storedHash == null) return true; // No PIN set yet
    return await _apiClient.verifyPin(pin, storedHash);
  }

  Future<bool> isBiometricAvailable() async {
    try {
      final bool canCheck = await _localAuth.canCheckBiometrics;
      final bool isDeviceSupported = await _localAuth.isDeviceSupported();
      return canCheck && isDeviceSupported;
    } catch (_) {
      return false;
    }
  }

  Future<bool> authenticateWithBiometrics() async {
    try {
      return await _localAuth.authenticate(
        localizedReason: 'Unlock your private conversation history',
        options: const AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: true,
        ),
      );
    } catch (_) {
      return false;
    }
  }

  Future<void> removePin() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_pinKey);
  }
}
