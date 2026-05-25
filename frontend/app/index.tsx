import { Ionicons } from "@expo/vector-icons";
import Slider from "@react-native-community/slider";
import {
  AudioModule,
  RecordingPresets,
  setAudioModeAsync,
  useAudioPlayer,
  useAudioPlayerStatus,
  useAudioRecorder,
  useAudioRecorderState,
} from "expo-audio";

import * as DocumentPicker from "expo-document-picker";
import { Directory, File, Paths } from "expo-file-system";
import { useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

export default function Index() {
  const audioRecorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  const recorderState = useAudioRecorderState(audioRecorder);

  const [isProcessing, setIsProcessing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  type RecordedFile = {
    name: string;
    duration: string;
    file: string | null;
  };
  const [recordedFile, setRecordedFile] = useState<RecordedFile | null>(null);
  const [backupFile, setBackupFile] = useState<RecordedFile | null>(null);
  const [temperature, setTemperature] = useState(0.3);

  const [generated, setGenerated] = useState(false);

  const player = useAudioPlayer(recordedFile?.file);
  const playerStatus = useAudioPlayerStatus(player);

  // Getting Input Section

  async function startRecording() {
    try {
      const status = await AudioModule.requestRecordingPermissionsAsync();
      console.log("start");
      if (status.granted) {
        await setAudioModeAsync({
          allowsRecording: true,
          playsInSilentMode: true,
        });
        await audioRecorder.prepareToRecordAsync();
        audioRecorder.record();
      }
    } catch (error) {
      alert(
        "Unable to record. Please ensure microphone permissions are granted.",
      );
    }
  }
  async function stopRecording() {
    setIsProcessing(true);

    console.log("stop");
    await audioRecorder.stop();

    await setAudioModeAsync({
      allowsRecording: false,
      playsInSilentMode: true,
    });

    let file = {
      name: "live-recording.m4a",
      duration: getDurationFormatted(recorderState.durationMillis),
      file: audioRecorder.uri,
    };

    setRecordedFile(file);
    setIsProcessing(false);
  }

  async function getDocument() {
    try {
      setIsProcessing(true);

      const result = await DocumentPicker.getDocumentAsync({
        type: "audio/*",
        copyToCacheDirectory: true,
      });

      if (result.canceled) {
        setIsProcessing(false);
        return;
      }

      const document = result.assets[0];
      const name = document.name;

      let file = {
        name: name ? name : "recordedfile",
        duration: "0",
        file: document.uri,
      };
      setRecordedFile(file);
      setIsProcessing(false);
      setBackupFile(file);
    } catch (error) {
      alert("Failed to load the file. Please try again.");
      console.error(error);
      setIsProcessing(false);
    }
  }

  function getDurationFormatted(milliseconds: number) {
    const minutes = milliseconds / 1000 / 60;
    const seconds = Math.round((minutes - Math.floor(minutes)) * 60);
    return seconds < 10
      ? `${Math.floor(minutes)}:0${seconds}`
      : `${Math.floor(minutes)}:${seconds}`;
  }
  // Where the magic happens
  async function generateMelody() {
    if (!recordedFile?.file) {
      alert("Please record or upload an audio file to proceed.");
      return;
    }
    try {
      setIsGenerating(true);
      let filename = recordedFile.name;
      //to make sure it has an extension
      if (!filename.includes(".")) filename = "recording.m4a";

      // i think we could do it without this line because we know what we are sending
      const ext = filename.split(".").pop()?.toLowerCase();
      const mimeType = ext === "mp3" ? "audio/mpeg" : "audio/mp4";

      const formData = new FormData();
      formData.append("file", {
        uri: recordedFile.file,
        name: filename,
        type: mimeType,
      } as any);

      // Sending request to the Flask server
      // Using the machine's local IP address so physical devices on the same network can connect
      const response = await fetch("http://192.168.1.244:5000/generate", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Server error:", response.status, errorText);
        alert(`An error occurred on the server (Status: ${response.status}).`);
        throw new Error(errorText);
      }

      // Read the echoed file bytes directly
      const responseBuffer = await response.arrayBuffer();
      const bytes = new Uint8Array(responseBuffer);

      // create directory if it deosnt exist

      const dir = new Directory(Paths.cache, "generated-melodies");
      if (!dir.exists) {
        dir.create();
      }
      // here just creating the file and putting it in the directory
      const timestamp = Date.now();
      const uniqueName = `melody-${timestamp}.wav`;

      const outputFile = new File(
        Paths.cache,
        `generated-melodies/${uniqueName}`,
      );
      outputFile.create();
      outputFile.write(bytes);

      setBackupFile(recordedFile);
      setRecordedFile({
        name: "generated.wav",
        duration: "0",
        file: outputFile.uri,
      });
      setGenerated(true);
    } catch (error) {
      console.error("Generation error:", error);
      alert(
        "An error occurred during generation: " +
          (error instanceof Error ? error.message : String(error)),
      );
    } finally {
      setIsGenerating(false);
    }
  }

  // Player Section
  const playRecording = () => {
    try {
      if (
        playerStatus.playbackState === "ended" ||
        playerStatus.currentTime >= (playerStatus.duration || 0)
      ) {
        player.seekTo(0);
      }
      player.play();
    } catch (error) {
      alert("Unable to play the audio file.");
    }
  };
  const stopPlaying = () => {
    try {
      player.pause();
    } catch (error) {}
  };
  const togglePlay = () => {
    if (playerStatus.playing) {
      stopPlaying();
    } else {
      playRecording();
    }
  };

  function getRecording() {
    if (!recordedFile) return;
    if (generated) return;

    return (
      <View>
        <View style={styles.recordingRow}>
          <View style={styles.underlineWrap}>
            <Pressable onPress={togglePlay}>
              <Text style={styles.playText}>
                {recordedFile.name} (
                {recordedFile.duration !== "0"
                  ? recordedFile.duration
                  : getDurationFormatted((playerStatus.duration || 0) * 1000)}
                )
              </Text>
            </Pressable>

            <View style={styles.purpleUnderline} />
          </View>

          <Pressable onPress={clearRecording} style={styles.clearButton}>
            <Ionicons name="close" size={32} color="black" />
          </Pressable>
        </View>
        <View
          style={{
            flexDirection: "row",
            alignItems: "center",
            gap: 12,
            marginBottom: 30,
          }}
        >
          <View style={{ flex: 1 }}>
            <Text
              style={{
                marginBottom: 6,
                fontFamily: "Inter_400Regular",
                fontSize: 13,
              }}
            >
              Generation Temperature: {temperature.toFixed(1)}
            </Text>

            <Slider
              style={{ width: "100%", height: 50 }}
              minimumValue={0.1}
              maximumValue={0.9}
              step={0.1}
              value={temperature}
              onValueChange={(temp) => setTemperature(temp)}
              minimumTrackTintColor="#3500B2"
              maximumTrackTintColor="#3500B2"
              thumbTintColor="#3500B2"
            />
          </View>

          <Pressable
            onPress={generateMelody}
            style={{
              width: 50,
              height: 50,
              borderRadius: 25,
              backgroundColor: "#3500B2",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            <Ionicons name="musical-note" size={24} color="#FFFFFF" />
          </Pressable>
        </View>
      </View>
    );
  }

  function clearGenerated() {
    setGenerated(false);
    setRecordedFile(null);
    setRecordedFile(backupFile);
  }

  function clearRecording() {
    setRecordedFile(null);
    stopPlaying();
  }

  if (isGenerating) {
    return (
      <View style={styles.generatingContainer}>
        <View style={styles.generatingIconCircle}>
          <Ionicons name="musical-note" size={32} color="#FFFFFF" />
        </View>
        <Text style={styles.generatingText}>Generating...</Text>
      </View>
    );
  }

  if (generated) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <Pressable onPress={clearGenerated} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="black" />
            <Text style={styles.backText}>Back</Text>
          </Pressable>
        </View>

        <View style={styles.centerBox}>
          <View style={styles.generatedIconCircle}>
            <Ionicons name="musical-notes" size={40} color="#FFFFFF" />
          </View>
          <Text style={styles.mainTextCentered}>
            Your composition has been successfully generated.
          </Text>

          <Pressable onPress={togglePlay} style={styles.bigPlayButton}>
            <Ionicons
              name={playerStatus.playing ? "pause" : "play"}
              size={40}
              color="white"
            />
          </Pressable>

          <Text style={styles.playText}>
            {recordedFile?.name} (
            {getDurationFormatted((playerStatus.duration || 0) * 1000)})
          </Text>
        </View>
        <View style={{ height: 100 }} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.mainBox}>
        <Text style={styles.mainText}>
          {recorderState.isRecording
            ? "Recording in progress..."
            : recordedFile
              ? "Configure the model temperature and generate your musical phrase."
              : "Record or upload a musical phrase to begin the generation process."}
        </Text>
      </View>

      <View style={styles.bottomBox}>
        {getRecording()}
        <Pressable
          onPress={recorderState.isRecording ? stopRecording : startRecording}
          style={styles.recordOuterCircle}
        >
          {recorderState.isRecording ? (
            <View style={styles.stopInner} />
          ) : (
            <View style={styles.recordInner} />
          )}
        </Pressable>
        <View style={styles.uploadRow}>
          <Text style={styles.uploadFileText}>Upload an audio file:</Text>

          <Pressable
            onPress={() => {
              getDocument();
            }}
            style={styles.uploadIconButton}
          >
            <Ionicons
              name="cloud-upload-outline"
              size={24}
              color="black"
              style={{ transform: [{ translateY: 8 }] }}
            />
          </Pressable>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "space-between",
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
    alignItems: "center",
  },

  recordOuterCircle: {
    width: 90,
    height: 90,
    borderRadius: 45,
    backgroundColor: "#FFFFFF",
    borderWidth: 5,
    borderColor: "#D7D7D7",
    justifyContent: "center",
    alignItems: "center",
  },

  recordInner: {
    width: 70,
    height: 70,
    borderRadius: 40,
    backgroundColor: "red",
  },

  stopInner: {
    width: 40,
    height: 40,
    borderRadius: 5,
    backgroundColor: "red",
  },

  uploadFileText: {
    fontFamily: "Inter_400Regular",
    fontSize: 13,
    marginTop: 15,
  },

  playText: {
    fontFamily: "Inter_400Regular",
    fontSize: 14,
    color: "black",
  },

  clearButton: {
    justifyContent: "center",
    alignItems: "center",
    height: 30,
  },

  recordingRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "flex-start",
    width: "100%",
    gap: 10,
    marginBottom: 20,
  },

  underlineWrap: {
    alignItems: "flex-start",
  },

  purpleUnderline: {
    height: 5,
    backgroundColor: "#3500B2",
    width: "100%",
    marginTop: 2,
  },
  greenUnderline: {
    height: 5,
    backgroundColor: "#00b22a",
    width: "100%",
    marginTop: 2,
  },

  uploadRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "flex-start",
    gap: 6,
    marginTop: 15,
  },

  uploadIconButton: {
    padding: 2,
    justifyContent: "center",
    alignItems: "center",
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    paddingTop: 60,
    paddingHorizontal: 20,
  },
  backButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  backText: {
    fontFamily: "Inter_400Regular",
    fontSize: 16,
    color: "black",
  },
  centerBox: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 40,
  },
  generatedIconCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: "#00b22a",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 30,
  },
  mainTextCentered: {
    fontFamily: "Inter_400Regular",
    fontSize: 24,
    textAlign: "center",
    marginBottom: 40,
  },
  bigPlayButton: {
    width: 90,
    height: 90,
    borderRadius: 45,
    backgroundColor: "#3500B2",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 20,
    // Add a slight shadow for depth
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
    elevation: 6,
  },
  generatingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#FFFFFF",
  },
  generatingIconCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: "#3500B2",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 20,
  },
  generatingText: {
    fontFamily: "Inter_400Regular",
    fontSize: 18,
    color: "#3500B2",
  },
});
