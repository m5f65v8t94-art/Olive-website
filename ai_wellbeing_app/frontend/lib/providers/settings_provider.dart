import 'package:flutter/material.dart';
import '../core/services/auth_service.dart';
import '../core/services/notification_service.dart';

class SettingsProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();
  final NotificationService _notificationService = NotificationService();

  bool _isPinSet = false;
  bool _notificationsEnabled = true;
  bool _isDisguised = false; // Emergency quick disguise state
  bool _isBiometricAvailable = false;

  bool get isPinSet => _isPinSet;
  bool get notificationsEnabled => _notificationsEnabled;
  bool get isDisguised => _isDisguised;
  bool get isBiometricAvailable => _isBiometricAvailable;

  Future<void> init() async {
    _isPinSet = await _authService.hasPinSet();
    _notificationsEnabled = await _notificationService.areNotificationsEnabled();
    _isBiometricAvailable = await _authService.isBiometricAvailable();
    notifyListeners();
  }

  void toggleDisguise() {
    _isDisguised = !_isDisguised;
    notifyListeners();
  }

  Future<void> setPin(String pin) async {
    await _authService.setPin(pin);
    _isPinSet = true;
    notifyListeners();
  }

  Future<bool> verifyPin(String pin) async {
    return await _authService.verifyPin(pin);
  }

  Future<bool> unlockWithBiometrics() async {
    return await _authService.authenticateWithBiometrics();
  }

  Future<void> removePin() async {
    await _authService.removePin();
    _isPinSet = false;
    notifyListeners();
  }

  Future<void> setNotificationsEnabled(bool enabled) async {
    await _notificationService.setNotificationsEnabled(enabled);
    _notificationsEnabled = enabled;
    notifyListeners();
  }
}
