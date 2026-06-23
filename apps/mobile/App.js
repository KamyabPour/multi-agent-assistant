import { StatusBar } from "expo-status-bar";
import { useState } from "react";
import { Button, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";

const API_BASE = process.env.EXPO_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export default function App() {
  const [message, setMessage] = useState("Help me build a balanced weekly routine.");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const runAssistant = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "mobile-user", message, context: {} }),
      });

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>Life Assistant Mobile</Text>
        <Text style={styles.subtitle}>Specialist agents coordinated through one backend</Text>

        <TextInput
          multiline
          style={styles.input}
          value={message}
          onChangeText={setMessage}
          placeholder="Ask your assistant"
        />

        <Button title={loading ? "Thinking..." : "Send"} onPress={runAssistant} disabled={loading} />

        {error ? <Text style={styles.error}>Error: {error}</Text> : null}

        {result ? (
          <View style={styles.card}>
            <Text style={styles.route}>Route: {result.route}</Text>
            <Text style={styles.summary}>{result.result.summary}</Text>
            {result.result.actions.map((action, idx) => (
              <Text key={`${action.title}-${idx}`} style={styles.action}>
                - {action.title}: {action.details}
              </Text>
            ))}
          </View>
        ) : null}
      </ScrollView>
      <StatusBar style="auto" />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f7f9fb" },
  content: { padding: 20, gap: 12 },
  title: { fontSize: 28, fontWeight: "700", color: "#12324a" },
  subtitle: { fontSize: 14, color: "#3f596b", marginBottom: 8 },
  input: {
    minHeight: 130,
    backgroundColor: "#fff",
    borderColor: "#d6dee5",
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    textAlignVertical: "top",
  },
  error: { color: "#b00020", marginTop: 8 },
  card: {
    marginTop: 16,
    backgroundColor: "#ffffff",
    borderRadius: 12,
    borderColor: "#d6dee5",
    borderWidth: 1,
    padding: 12,
  },
  route: { fontSize: 16, fontWeight: "700", marginBottom: 6 },
  summary: { fontSize: 14, marginBottom: 8 },
  action: { fontSize: 14, marginTop: 4 },
});
