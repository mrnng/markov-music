import React, { useEffect, useState } from "react";
import { StyleSheet } from "react-native";
import {
	RecordingPresets,
	AudioModule,
	useAudioPlayer,
	useAudioRecorder,
	useAudioRecorderState,
	setAudioModeAsync,
	useAudioPlayerStatus,
} from "expo-audio";
import { Ionicons } from "@expo/vector-icons";
import AntDesign from "@expo/vector-icons/AntDesign";
import EvilIcons from "@expo/vector-icons/EvilIcons";
import { Alert, Text, FlatList, View, TouchableOpacity } from "react-native";
import * as DocumentPicker from "expo-document-picker";

interface Recording {
	// URI is to get the local path of the audio
	id: string;
	URI: string;
	duration: number;
}

export default function Recorder() {
	const [recording, setRecording] = useState<Recording | null>(null);
	const [isRecording, setIsRecording] = useState(false);
	const [bars, setBars] = useState(1);
	const audioRecorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
	const player = useAudioPlayer(recording?.URI);
	const recorderState = useAudioRecorderState(audioRecorder);
	const playerStatus = useAudioPlayerStatus(player);

	const requestPermissions = async () => {
		//asks the user fo permissions and returns Premissionsresponse
		//it has  status and status is either granted , undetermined pr denied
		const { status } = await AudioModule.requestRecordingPermissionsAsync();
		if (status !== "granted") {
			Alert.alert("You will not be able to use the recording features.");
			return;
		}
		setAudioModeAsync({
			playsInSilentMode: true,
			allowsRecording: true,
		});
	};
	useEffect(() => {
		requestPermissions();
	}, []);

	const decrement = () => {
		if (bars == 1) {
			setBars(1);
		} else {
			setBars(bars - 1);
		}
	};
	const increment = () => {
		if (bars == 12) {
			setBars(12);
		} else {
			setBars(bars + 1);
		}
	};

	const startREC = async () => {
		try {
			// i just got this from the example on createAsync it should let us record
			await audioRecorder.prepareToRecordAsync();
			audioRecorder.record();
			setIsRecording(true);
		} catch (E) {
			console.error("Error while recording audio.", E);
			Alert.alert("Error while recording audio.");
		}
	};

	const stopREC = async () => {
		try {
			setIsRecording(false);
			await audioRecorder.stop();
			if (audioRecorder.uri) {
				const newRecording: Recording = {
					id: Date.now().toString(),
					URI: audioRecorder.uri,
					duration: Math.round(recorderState.durationMillis / 1000),
				};
				setRecording(newRecording);
			}
		} catch (E) {
			console.error("Could not save the recording.", E);
			Alert.alert("Could not save the recording.");
		}
	};
	const deleteRecording = () => {
		if (playerStatus.playing) stopPlaying();
		setRecording(null);
	};
	//get the file
	const getDocument = async () => {
		try {
			const result = await DocumentPicker.getDocumentAsync({
				type: "audio/*",
			});

			if (result.canceled) return;
			deleteRecording();

			const file = result.assets[0];
			const newRecording: Recording = {
				id: file.name,
				URI: file.uri,
				duration: 0,
			};
			setRecording(newRecording);
		} catch (error) {
			Alert.alert("failed to load file");
		}
	};

	const playRecording = () => {
		try {
			if (playerStatus.currentTime == playerStatus.duration)
				player.seekTo(0);
			player.play();
		} catch (error) {
			Alert.alert("Failed to play recording.");
		}
	};
	const stopPlaying = () => {
		try {
			player.pause();
		} catch (error) {}
	};
	const toggleREC = () => {
		if (isRecording) {
			stopREC();
		} else {
			startREC();
		}
	};
	const togglePlay = () => {
		if (playerStatus.playing) {
			stopPlaying();
		} else {
			playRecording();
		}
	};

	return (
		<View style={styles.container}>
			{recording ? <Text>{recording.id}</Text> : <></>}
			<View>
				{recording === null ? (
					// no recording found so record
					<TouchableOpacity
						onPress={toggleREC}
						style={styles.iconCircle}
					>
						{isRecording ? (
							<Ionicons
								style={styles.musicIcon}
								name="stop"
								size={64}
								color="#ccc"
							/>
						) : (
							<Ionicons
								style={styles.musicIcon}
								name="mic"
								size={64}
								color="#ccc"
							/>
						)}
					</TouchableOpacity>
				) : (
					// there is recording so play
					<View style={styles.playdel}>
						<TouchableOpacity
							onPress={togglePlay}
							style={styles.iconCircle}
						>
							{playerStatus.playing ? (
								<Ionicons
									style={styles.musicIcon}
									name="pause"
									size={64}
									color="#ccc"
								/>
							) : (
								<Ionicons
									style={styles.musicIcon}
									name="play"
									size={64}
									color="#ccc"
								/>
							)}
						</TouchableOpacity>
						<TouchableOpacity onPress={deleteRecording}>
							<EvilIcons
								style={styles.musicIcon}
								name="trash"
								size={64}
								color="#ccc"
							/>
						</TouchableOpacity>
					</View>
				)}
			</View>
			<View style={styles.counterContainer}>
				<Text style={styles.barsLabel}>Upload file instead:</Text>
				<TouchableOpacity
					style={styles.fileButton}
					onPress={getDocument}
				>
					<AntDesign name="file-add" size={20} color="black" />
				</TouchableOpacity>
			</View>

			<Text style={styles.barsLabel}>Number of Bars</Text>

			<View style={styles.counterContainer}>
				<TouchableOpacity
					style={styles.counterButton}
					onPress={decrement}
				>
					<Text style={styles.counterButtonText}>-</Text>
				</TouchableOpacity>

				<View style={styles.numberDisplay}>
					<Text style={styles.numberText}>{bars}</Text>
				</View>

				<TouchableOpacity
					style={styles.counterButton}
					onPress={increment}
				>
					<Text style={styles.counterButtonText}>+</Text>
				</TouchableOpacity>
			</View>
			<Text style={styles.subtitle}>(1~12)</Text>
			<TouchableOpacity style={styles.generateButton}>
				<Text style={styles.generateButtonText}>Genarate</Text>
			</TouchableOpacity>
		</View>
	);
}

const styles = StyleSheet.create({
	container: {
		flex: 1,
		backgroundColor: "#FFFFFF",
		alignItems: "center",
		paddingTop: 60,
	},

	iconCircle: {
		width: 120,
		height: 120,
		borderRadius: 60,
		backgroundColor: "#FFFFFF",
		justifyContent: "center",
		alignItems: "center",
		shadowColor: "#000",
		shadowOffset: { width: 4, height: 4 },
		shadowOpacity: 0.1,
		shadowRadius: 8,
		elevation: 5,
		marginBottom: 40,
	},

	musicIcon: {
		fontSize: 40,
		color: "#000000",
	},

	playdel: {
		flexDirection: "row",
	},

	barsLabel: {
		fontSize: 16,
		fontWeight: "600",
		color: "#000000",
		letterSpacing: 2,
		marginBottom: 8,
	},

	counterContainer: {
		display: "flex",
		flexDirection: "row",
		alignItems: "center",
		marginBottom: 8,
	},

	counterButton: {
		width: 32,
		height: 32,
		borderRadius: 12,
		backgroundColor: "#000000",
		justifyContent: "center",
		alignItems: "center",
	},

	counterButtonText: {
		color: "#FFFFFF",
		fontSize: 40,
		fontWeight: "bold",
	},

	numberDisplay: {
		width: 80,
		height: 40,
		backgroundColor: "#F5F5F5",
		borderRadius: 12,
		justifyContent: "center",
		alignItems: "center",
		marginHorizontal: 20,
	},

	numberText: {
		fontSize: 24,
		fontWeight: "bold",
		color: "#000000",
	},
	fileButton: {
		width: 20,
		height: 20,
		borderRadius: 12,
		backgroundColor: "#FFFFFF",
		justifyContent: "center",
		alignItems: "center",
	},

	subtitle: {
		fontSize: 12,
		color: "#666666",
		marginBottom: 60,
	},

	generateButton: {
		width: 200,
		height: 48,
		backgroundColor: "#000000",
		borderRadius: 12,
		justifyContent: "center",
		alignItems: "center",
		shadowColor: "#000",
		shadowOffset: { width: 2, height: 2 },
		shadowOpacity: 0.3,
		shadowRadius: 8,
		elevation: 5,
	},

	generateButtonText: {
		color: "#FFFFFF",
		fontSize: 16,
		fontWeight: "600",
		letterSpacing: 1,
	},
});
