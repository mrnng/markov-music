import { Pressable, StyleSheet, Text, View } from "react-native";

export default function Index() {
  return (
    <View style={styles.container}>
      <View style={styles.mainBox}>
        <Text style={styles.mainText}>
          Record or upload a musical phrase. We'll help you get inspired.
        </Text>
      </View>

      <View style={styles.bottomBox}>
        <Pressable>
          <Text>Record</Text>
        </Pressable>

        <Pressable>
          <Text>Upload File</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "#FFFFFF",
  },

  mainBox: {
    marginTop: 20,
    padding: 20,
  },

  mainText: {
    fontFamily: "Inter_400Regular",
    fontSize: 35,
  },

  bottomBox: {
    marginBottom: 100,
    padding: 20,
  },
});
