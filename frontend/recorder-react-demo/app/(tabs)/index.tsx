import { useEffect, useState } from "react";
import { Audio } from "expo-av";
import { Alert, Text, FlatList, View } from "react-native";
import { Recording } from "expo-av/build/Audio";

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
	const [isPlayingID, setIsPlayingID] = useState<string | null>(null);

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

		useEffect(() => {
			return () => {
				if (sound) sound.unloadAsync(); // this is to unload the memory
			};
		}, []);
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

	const playRecording = async (REC: newRecording) => {
		try {
			if (sound) {
				await sound.stopAsync();
				await sound.unloadAsync();
				setSound(null);
				setIsPlayingID(null);
			}

			const { sound: newSound } = await Audio.Sound.createAsync(
				{ uri: REC.URI },
				{ shouldPlay: true },
			);

			setSound(newSound);
			setIsPlayingID(REC.id);
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
		<View>
			<button onClick={() => playRecording(item)}></button>
		</View>
	);
	return (
		<View>
			<View>
				<Text>record</Text>
				<button onClick={toggleREC}>
					{isRecording ? "Stop " : "Start"}
				</button>
			</View>
			<View>
				{recordings.length === 0 ? (
					<View>
						<Text>No recordings yet</Text>
						<Text>Tap the button above to start</Text>
					</View>
				) : (
					<FlatList
						data={recordings}
						renderItem={renderRecordingItem}
						keyExtractor={(item) => item.id}
						showsVerticalScrollIndicator={false}
					/>
				)}
			</View>
		</View>
	);
}
