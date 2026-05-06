import {
  Inter_400Regular,
  Inter_700Bold,
  useFonts,
} from "@expo-google-fonts/inter";
import { Link, Stack } from "expo-router";
import { Pressable, Text } from "react-native";

export default function RootLayout() {
  const [fontsLoaded] = useFonts({
    Inter_400Regular,
    Inter_700Bold,
  });

  if (!fontsLoaded) {
    return <Text>Loading...</Text>;
  }

  return (
    <Stack
      screenOptions={{
        headerShadowVisible: false,
      }}
    >
      <Stack.Screen
        name="index"
        options={{
          title: "Markov Music",
          headerTitleStyle: {
            fontFamily: "Inter_700Bold",
          },
          headerRight: () => (
            <Link href="/list" asChild>
              <Pressable>
                <Text
                  style={{
                    color: "black",
                    marginRight: 10,
                    fontFamily: "Inter_400Regular",
                    fontSize: 18,
                  }}
                >
                  List
                </Text>
              </Pressable>
            </Link>
          ),
        }}
      />
      <Stack.Screen
        name="list"
        options={{
          title: "List",
          headerTitleStyle: {
            fontFamily: "Inter_700Bold",
          },
        }}
      />
    </Stack>
  );
}
