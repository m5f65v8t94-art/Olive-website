enum ConversationMode {
  justListen,
  giveMeAdvice,
  helpMeUnderstand,
  helpMeTellSomeone;

  String get apiValue {
    switch (this) {
      case ConversationMode.justListen:
        return "just_listen";
      case ConversationMode.giveMeAdvice:
        return "give_me_advice";
      case ConversationMode.helpMeUnderstand:
        return "help_me_understand";
      case ConversationMode.helpMeTellSomeone:
        return "help_me_tell_someone";
    }
  }

  static ConversationMode fromString(String value) {
    switch (value) {
      case "give_me_advice":
        return ConversationMode.giveMeAdvice;
      case "help_me_understand":
        return ConversationMode.helpMeUnderstand;
      case "help_me_tell_someone":
        return ConversationMode.helpMeTellSomeone;
      case "just_listen":
      default:
        return ConversationMode.justListen;
    }
  }

  String get displayName {
    switch (this) {
      case ConversationMode.justListen:
        return "Just Listen";
      case ConversationMode.giveMeAdvice:
        return "Give Me Advice";
      case ConversationMode.helpMeUnderstand:
        return "Help Me Understand";
      case ConversationMode.helpMeTellSomeone:
        return "Help Me Tell Someone";
    }
  }

  String get description {
    switch (this) {
      case ConversationMode.justListen:
        return "Listen without unsolicited advice or rush.";
      case ConversationMode.giveMeAdvice:
        return "Gentle, realistic coping suggestions.";
      case ConversationMode.helpMeUnderstand:
        return "Reflect and unpack emotions without labels.";
      case ConversationMode.helpMeTellSomeone:
        return "Craft a comfortable message for a trusted person.";
    }
  }
}
