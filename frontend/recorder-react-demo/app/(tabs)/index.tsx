import React, { useEffect, useState } from "react";
import { StyleSheet } from "react-native";
import { Audio } from "expo-av";
import { Ionicons } from "@expo/vector-icons";
import EvilIcons from "@expo/vector-icons/EvilIcons";
import { Alert, Text, FlatList, View, TouchableOpacity } from "react-native";

interface newRecording {
	// URI is to get the local path of the audio
	id: string;
	URI: string;
	duration: number;
}

export default function Recorder() {
	const [recording, setRecording] = useState<Audio.Recording | null>(null);
	const [recordings, setRecordings] = useState<newRecording[]>([]);
	const [isRecording, setIsRecording] = useState(false);
	const [sound, setSound] = useState<Audio.Sound | null>(null);
	const [bars, setBars] = useState(1);

	const requestPermissions = async () => {
		//asks the user fo permissions and returns Premissionsresponse
		//it has  status and status is either granted , undetermined pr denied
		const { status } = await Audio.requestPermissionsAsync();
		if (status !== "granted") {
			Alert.alert(
				"bruh its an audio recorder how would we record the audio with no mic ",
			);
			return;
		}
	};
	useEffect(() => {
		requestPermissions();
		return () => {
			if (sound) sound.unloadAsync(); // this is to unload the memory
		};
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
			const { recording: recordingObject, status } =
				await Audio.Recording.createAsync(
					Audio.RecordingOptionsPresets.HIGH_QUALITY,
				);
			setRecording(recordingObject);
			setIsRecording(true);
		} catch (E) {
			console.error("no happon record there is probrem", E);
			Alert.alert("ERROR COULDNT RECORED");
		}
	};

	const stopREC = async () => {
		if (!recording) return;
		try {
			setIsRecording(false);

			const status = await recording.stopAndUnloadAsync();
			const URI = recording.getURI();
			const duration = status.durationMillis;

			if (URI) {
				const newRecording: newRecording = {
					id: Date.now().toString(),
					URI,
					duration: duration,
				};
				setRecordings((prev) => [newRecording, ...prev]);
			}

			setRecording(null);
		} catch (E) {
			console.error("RECORDING OVERLOADDDD AHHHHHHHHHH", E);
			Alert.alert("couldnt save the recording");
		}
	};
	const deleteRecording = (id: string) => {
		setRecordings((prev) => prev.filter((rec) => rec.id !== id));
	};

	const playRecording = async (REC: newRecording) => {
		try {
			if (sound) {
				await sound.stopAsync();
				await sound.unloadAsync();
				setSound(null);
			}

			const { sound: newSound } = await Audio.Sound.createAsync(
				{ uri: REC.URI },
				{ shouldPlay: true },
			);

			setSound(newSound);
		} catch (error) {
			Alert.alert("failed to play ");
		}
	};
	const toggleREC = () => {
		if (isRecording) {
			stopREC();
		} else {
			startREC();
		}
	};
	const renderRecordingItem = ({ item }: { item: newRecording }) => (
		<View style={styles.playContainer}>
			<TouchableOpacity onPress={() => playRecording(item)}>
				<Text>
					play id:{item.id} {item.duration}
				</Text>
			</TouchableOpacity>
			<TouchableOpacity onPress={() => deleteRecording(item.id)}>
				<EvilIcons name="trash" size={24} color="black" />
			</TouchableOpacity>
		</View>
	);
	return (
		<View style={styles.container}>
			<View>
				<TouchableOpacity onPress={toggleREC} style={styles.iconCircle}>
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
							name="musical-note"
							size={64}
							color="#ccc"
						/>
					)}
				</TouchableOpacity>
			</View>

			<Text style={styles.barsLabel}>BARS</Text>

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
			<View>
				{recordings.length === 0 ? (
					<View style={styles.subtitle}>
						<Text>No recordings yet</Text>
					</View>
				) : (
					<FlatList
						data={recordings}
						renderItem={renderRecordingItem}
						keyExtractor={(item) => item.id}
						showsVerticalScrollIndicator={false}
						style={styles.listContent}
					/>
				)}
			</View>
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

	barsLabel: {
		fontSize: 16,
		fontWeight: "600",
		color: "#000000",
		letterSpacing: 2,
		marginBottom: 8,
	},

	counterContainer: {
		flexDirection: "row",
		alignItems: "center",
		marginBottom: 4,
	},

	counterButton: {
		width: 32,
		height: 32,
		borderRadius: 16,
		backgroundColor: "#000000",
		justifyContent: "center",
		alignItems: "center",
	},

	counterButtonText: {
		color: "#FFFFFF",
		fontSize: 20,
		fontWeight: "bold",
	},

	numberDisplay: {
		width: 80,
		height: 40,
		backgroundColor: "#F5F5F5",
		borderRadius: 20,
		justifyContent: "center",
		alignItems: "center",
		marginHorizontal: 20,
	},

	numberText: {
		fontSize: 24,
		fontWeight: "bold",
		color: "#000000",
	},

	subtitle: {
		fontSize: 12,
		color: "#666666",
		marginBottom: 60,
	},

	listContent: {
		gap: 12,
	},

	generateButton: {
		width: 200,
		height: 48,
		backgroundColor: "#000000",
		borderRadius: 24,
		justifyContent: "center",
		alignItems: "center",
	},

	generateButtonText: {
		color: "#FFFFFF",
		fontSize: 16,
		fontWeight: "600",
		letterSpacing: 1,
	},
	playContainer: {
		flexDirection: "row",
		alignItems: "center",
		marginBottom: 4,
	},
});
