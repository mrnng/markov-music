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
import React from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import * as DocumentPicker from "expo-document-picker";
import { File, Directory, Paths } from "expo-file-system";

export default function Index() {
  const audioRecorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  const recorderState = useAudioRecorderState(audioRecorder);

<<<<<<< HEAD
  const [isProcessing, setIsProcessing] = React.useState(false);
  type RecordedFile = {
    name: string;
    duration: string;
    file: string | null;
  };
  const [recordedFile, setRecordedFile] = React.useState<RecordedFile | null>(
    null,
  );
  const [temperature, setTemperature] = React.useState(0.3);

  const player = useAudioPlayer(recordedFile?.file);
  const playerStatus = useAudioPlayerStatus(player);
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
    } catch (error) {}
  }

  async function stopRecording() {
    setIsProcessing(true);
    console.log("stop");
    await audioRecorder.stop();
=======
	const [isProcessing, setIsProcessing] = useState(false);
	type RecordedFile = {
		name: string;
		duration: string;
		file: string | null;
	};
	const [recordedFile, setRecordedFile] = useState<RecordedFile | null>(null);
	const [temperature, setTemperature] = useState(0.3);

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
		} catch (error) {}
	}
	async function stopRecording() {
		setIsProcessing(true);

		console.log("stop");
		await audioRecorder.stop();
>>>>>>> abb098b6844cd433aa7585d5ae98ac7011ff1e9d

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
      const name = document.file?.name;

      let file = {
        name: name ? name : "recordedfile",
        duration: "0",
        file: document.uri,
      };
      setRecordedFile(file);
      setIsProcessing(false);
    } catch (error) {
      alert("failed to load file");
      console.error(error);
      setIsProcessing(false);
    }
  }

<<<<<<< HEAD
  function getDurationFormatted(milliseconds: number) {
    const minutes = milliseconds / 1000 / 60;
    const seconds = Math.round((minutes - Math.floor(minutes)) * 60);
    return seconds < 10
      ? `${Math.floor(minutes)}:0${seconds}`
      : `${Math.floor(minutes)}:${seconds}`;
  }
  const playRecording = () => {
    try {
      if (playerStatus.currentTime == playerStatus.duration) player.seekTo(0);
      player.play();
    } catch (error) {
      alert("Failed to play recording.");
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
=======
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
			alert("please record or upload audio");
			return;
		}
		try {
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
			// just put your ip when you run the backend
			const response = await fetch(`${"YOUR IP"}/generate`, {
				method: "POST",
				body: formData,
			});

			if (!response.ok) {
				const errorText = await response.text();
				console.error("Server error:", response.status, errorText);
				alert(`Server error ${response.status}`);
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
			const uniqueName = `melody-${timestamp}.mid`;

			const outputFile = new File(
				Paths.cache,
				` generated-melodies/${uniqueName}`,
			);
			outputFile.create();
			outputFile.write(bytes);

			setRecordedFile({
				name: "generated-melody.mid",
				duration: "0",
				file: outputFile.uri,
			});
		} catch (error) {
			console.error("Generation error:", error);
			alert(
				"Failed: " +
					(error instanceof Error ? error.message : String(error)),
			);
		}
	}

	// Player Section
	const playRecording = () => {
		try {
			if (playerStatus.currentTime == playerStatus.duration)
				player.seekTo(0);
			player.play();
		} catch (error) {
			alert("Failed to play recording.");
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
>>>>>>> abb098b6844cd433aa7585d5ae98ac7011ff1e9d

  function getRecording() {
    if (!recordedFile) return;

    return (
      <View>
        <View style={styles.recordingRow}>
          <View style={styles.underlineWrap}>
            <Pressable onPress={togglePlay}>
              <Text style={styles.playText}>
                {recordedFile.name} ({recordedFile.duration})
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
              Temperature: {temperature.toFixed(1)}
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

<<<<<<< HEAD
          <Pressable
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
=======
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
						<Ionicons
							name="musical-note"
							size={24}
							color="#FFFFFF"
						/>
					</Pressable>
				</View>
			</View>
		);
	}
>>>>>>> abb098b6844cd433aa7585d5ae98ac7011ff1e9d

  function clearRecording() {
    setRecordedFile(null);
  }

  return (
    <View style={styles.container}>
      <View style={styles.mainBox}>
        <Text style={styles.mainText}>
          {recorderState.isRecording
            ? "Recording..."
            : isProcessing
              ? "Choose the temperature of the model and generate a phrase!"
              : recordedFile
                ? "Choose the temperature of the model and generate a phrase!"
                : "Record or upload a musical phrase. We'll help you get inspired."}
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
          <Text style={styles.uploadFileText}>Upload file instead:</Text>

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
});
