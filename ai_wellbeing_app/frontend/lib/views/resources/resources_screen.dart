import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/constants/app_strings.dart';

class ResourcesScreen extends StatelessWidget {
  const ResourcesScreen({super.key});

  final List<Map<String, dynamic>> _privateHelpServices = const [
    {
      "name": "Tele-MANAS",
      "subtitle": "Mental Health & Emotional Support",
      "desc": "Free, 24/7 comprehensive tele-mental health counseling by government healthcare professionals in multiple languages.",
      "phone": "14416",
      "alt_phone": "1800-89-14416",
      "has_whatsapp": false,
      "badge": "24/7 Toll-Free",
      "badge_color": Color(0xFF16A34A),
    },
    {
      "name": "Child Helpline",
      "subtitle": "Children & Teenagers (Up to 18)",
      "desc": "National 24-hour emergency phone outreach and protection service for children and teens in need of care or support.",
      "phone": "1098",
      "alt_phone": null,
      "has_whatsapp": false,
      "badge": "24/7 Free for Youth",
      "badge_color": Color(0xFF0284C7),
    },
    {
      "name": "Meri Trustline",
      "subtitle": "Online Safety, Bullying & Harassment",
      "desc": "Specialized, confidential support for young people facing online safety issues, cyberbullying, digital threats, or non-consensual personal content.",
      "phone": "6363 17 6363",
      "alt_phone": null,
      "has_whatsapp": true,
      "whatsapp_num": "916363176363",
      "badge": "Call & WhatsApp",
      "badge_color": Color(0xFF7C3AED),
    },
    {
      "name": "National Cyber Crime Helpline",
      "subtitle": "Cybercrime & Online Fraud",
      "desc": "Dedicated government helpline to report digital fraud, hacking, stalking, or serious digital crime (cybercrime.gov.in).",
      "phone": "1930",
      "alt_phone": null,
      "has_whatsapp": false,
      "badge": "24/7 National Portal",
      "badge_color": Color(0xFF475569),
    },
    {
      "name": "Emergency Services",
      "subtitle": "Immediate Physical Danger",
      "desc": "Single emergency number for police, ambulance, or fire assistance when your life or physical safety is in immediate danger.",
      "phone": "112",
      "alt_phone": null,
      "has_whatsapp": false,
      "badge": "Immediate Danger",
      "badge_color": AppColors.crisisRed,
    },
  ];

  final List<Map<String, dynamic>> _copingExercises = const [
    {
      "title": "4-7-8 Relaxing Breath",
      "desc": "Gently settles a fast heartbeat and soothes racing thoughts.",
      "steps": [
        "1. Inhale quietly through your nose for 4 seconds.",
        "2. Hold your breath gently for 7 seconds.",
        "3. Exhale completely through your mouth for 8 seconds.",
        "4. Repeat 4 times.",
      ]
    },
    {
      "title": "5-4-3-2-1 Sensory Grounding",
      "desc": "Brings your mind back into the room when feeling overwhelmed.",
      "steps": [
        "• 5 things you can SEE around you.",
        "• 4 things you can physically TOUCH or feel.",
        "• 3 things you can HEAR.",
        "• 2 things you can SMELL.",
        "• 1 positive thing you appreciate about yourself.",
      ]
    },
  ];

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Get Help (Privately)", style: TextStyle(fontWeight: FontWeight.w600)),
      ),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          // Calm, Private Guidance Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: isDark
                    ? [const Color(0xFF1E293B), const Color(0xFF0F172A)]
                    : [const Color(0xFFF0FDF4), const Color(0xFFE0F2FE)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: isDark ? Colors.white12 : const Color(0xFFBBF7D0)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.privacy_tip_outlined, color: AppColors.accentSage, size: 22),
                    SizedBox(width: 8),
                    Text("Private Real-World Support", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  ],
                ),
                const SizedBox(height: 8),
                const Text(
                  "If you are dealing with emotional distress, mental health challenges, online bullying, or safety concerns, support is available from trained, compassionate professionals.",
                  style: TextStyle(fontSize: 13, height: 1.45),
                ),
                const SizedBox(height: 12),

                // Confidentiality Guidance Note
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: isDark ? Colors.black26 : Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.black.withOpacity(0.06)),
                  ),
                  child: const Text(
                    "💡 Ask About Confidentiality: You are always welcome to ask any helpline counselor: 'What is your confidentiality policy?' before sharing personal details. Remember that services are legally bound to protect life in immediate danger; we do not promise absolute secrecy or complete anonymity.",
                    style: TextStyle(fontSize: 12, height: 1.4, color: Colors.grey),
                  ),
                ),
                const SizedBox(height: 10),

                // Trusted Adult Encouragement
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppColors.accentSage.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Text(
                    "🤝 Involving Someone You Trust: Whenever you feel safe doing so, we gently encourage involving a trusted parent, guardian, teacher, or adult in your life.",
                    style: TextStyle(fontSize: 12, height: 1.4, color: AppColors.accentSage, fontWeight: FontWeight.w600),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Helplines Section
          const Text("Confidential Helplines & Services", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17)),
          const SizedBox(height: 4),
          const Text("Easy Call and WhatsApp options where available:", style: TextStyle(fontSize: 13, color: Colors.grey)),
          const SizedBox(height: 12),

          ..._privateHelpServices.map((service) => Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(service["name"], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                                Text(service["subtitle"], style: const TextStyle(fontSize: 12, color: Colors.grey)),
                              ],
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: (service["badge_color"] as Color).withOpacity(0.12),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              service["badge"],
                              style: TextStyle(fontSize: 11, color: service["badge_color"], fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(service["desc"], style: const TextStyle(fontSize: 13, height: 1.4)),
                      const SizedBox(height: 12),

                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: [
                          ElevatedButton.icon(
                            onPressed: () {},
                            icon: const Icon(Icons.phone, size: 16),
                            label: Text("Call ${service["phone"]}"),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: service["name"] == "Emergency Services"
                                  ? AppColors.crisisRed
                                  : (service["badge_color"] as Color),
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                              textStyle: const TextStyle(fontSize: 13),
                            ),
                          ),
                          if (service["alt_phone"] != null)
                            OutlinedButton.icon(
                              onPressed: () {},
                              icon: const Icon(Icons.phone, size: 16),
                              label: Text("Call ${service["alt_phone"]}"),
                              style: OutlinedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                                textStyle: const TextStyle(fontSize: 13),
                              ),
                            ),
                          if (service["has_whatsapp"] == true)
                            ElevatedButton.icon(
                              onPressed: () {},
                              icon: const Icon(Icons.chat, size: 16),
                              label: const Text("Chat on WhatsApp"),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF25D366),
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                                textStyle: const TextStyle(fontSize: 13),
                              ),
                            ),
                        ],
                      ),
                    ],
                  ),
                ),
              )),

          const SizedBox(height: 20),
          const Divider(),
          const SizedBox(height: 16),

          // Grounding Exercises
          const Text("Grounding & Calming Exercises", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17)),
          const SizedBox(height: 12),

          ..._copingExercises.map((ex) => Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ExpansionTile(
                  title: Text(ex["title"], style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15)),
                  subtitle: Text(ex["desc"], style: const TextStyle(fontSize: 12, color: Colors.grey)),
                  children: [
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: (ex["steps"] as List<String>)
                            .map((step) => Padding(
                                  padding: const EdgeInsets.symmetric(vertical: 4.0),
                                  child: Text(step, style: const TextStyle(fontSize: 14, height: 1.4)),
                                ))
                            .toList(),
                      ),
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }
}
