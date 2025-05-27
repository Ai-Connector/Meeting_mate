import Head from 'next/head';
import { useState } from 'react';
import grpcClient from '../lib/grpcClient'; // Adjusted path
import {
  InitialSetup,
  MeetingStreamRequest,
  MeetingStreamResponse,
  MeetingInitialized,
  SaveMetadataRequest, // Import SaveMetadataRequest
} from '../generated/meeting_pb'; // Adjusted path
import styles from '@/styles/Home.module.css'; // Assuming default styles are still wanted

export default function Home() {
  const [meetingTitle, setMeetingTitle] = useState('');
  const [serverMessages, setServerMessages] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const startMeeting = () => {
    if (!meetingTitle.trim()) {
      alert('Please enter a meeting title.');
      return;
    }

    setServerMessages([]);
    setIsLoading(true);

    const metadata = new SaveMetadataRequest();
    metadata.setTitle(meetingTitle);
    // metadata.setMeetingDate(new Date().toISOString()); // Optional: set meeting date
    // metadata.addAttendees("User1"); // Optional: add attendees

    const initialSetup = new InitialSetup();
    initialSetup.setAudioFormat('wav');
    initialSetup.setMetadata(metadata); // Set the metadata

    const request = new MeetingStreamRequest();
    request.setInitialSetup(initialSetup);

    const stream = grpcClient.processMeeting();

    stream.on('data', (response: MeetingStreamResponse) => {
      setIsLoading(false);
      const initialized = response.getConfirmation(); // This is MeetingInitialized
      const partialTranscription = response.getPartialTranscription();
      const finalTranscription = response.getFinalTranscription();
      const summaryResult = response.getSummaryResult();
      const error = response.getError();

      if (initialized) {
        setServerMessages(prev => [
          ...prev,
          `Meeting Initialized: ID - ${initialized.getMeetingId()}, Message - ${initialized.getMessage()}, Success - ${initialized.getSuccess()}`,
        ]);
      } else if (partialTranscription) {
        setServerMessages(prev => [
          ...prev,
          `Partial Transcription (seq: ${partialTranscription.getSequenceNumber()}, interim: ${partialTranscription.getIsInterim()}): ${partialTranscription.getTranscriptSegment()}`,
        ]);
      } else if (finalTranscription) {
        setServerMessages(prev => [
          ...prev,
          `Final Transcription: ${finalTranscription.getFullTranscript()}`,
        ]);
      } else if (summaryResult) {
        setServerMessages(prev => [
          ...prev,
          `Summary: ${summaryResult.getSummaryText()}`,
        ]);
      } else if (error) {
        setServerMessages(prev => [
            ...prev,
            `Stream Error: Code ${error.getCode()}, Message: ${error.getMessage()}`,
        ]);
      } else {
        setServerMessages(prev => [
            ...prev,
            `Received an unknown message type from server.`,
        ]);
      }
    });

    stream.on('error', (err: any) => { // err type can be grpc.ServiceError
      setIsLoading(false);
      console.error('Stream Error:', err);
      setServerMessages(prev => [...prev, `Error: ${err.message}`]);
    });

    stream.on('end', () => {
      setIsLoading(false);
      console.log('Stream ended');
      setServerMessages(prev => [...prev, 'Stream ended.']);
    });

    stream.write(request);
    // stream.end(); // Do not end the stream immediately if client needs to send more data (e.g. audio chunks)
    // For this initial setup, we send one message and wait for responses.
    // If the client is only sending initial setup and then listening,
    // then perhaps the server closes the stream from its end after some time or an explicit client action.
    // For now, let's assume the stream stays open for other potential messages or needs explicit closing later.
  };

  return (
    <>
      <Head>
        <title>gRPC Meeting Client</title>
        <meta name="description" content="Frontend for gRPC meeting service" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}> {/* Using existing styles.main for layout */}
        <h1>Meeting Transcription Service</h1>

        <div>
          <input
            type="text"
            value={meetingTitle}
            onChange={(e) => setMeetingTitle(e.target.value)}
            placeholder="Enter Meeting Title"
            disabled={isLoading}
            style={{ marginRight: '10px', padding: '8px' }}
          />
          <button onClick={startMeeting} disabled={isLoading} style={{ padding: '8px 15px' }}>
            {isLoading ? 'Connecting...' : 'Start Meeting'}
          </button>
        </div>

        <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '10px', minHeight: '100px', background: '#f9f9f9' }}>
          <h2>Server Messages:</h2>
          {serverMessages.length === 0 && !isLoading && <p>No messages yet. Click "Start Meeting" to connect.</p>}
          {isLoading && <p>Waiting for server response...</p>}
          <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
            {serverMessages.map((msg, index) => (
              <div key={index} style={{ marginBottom: '5px', borderBottom: '1px solid #eee', paddingBottom: '5px' }}>{msg}</div>
            ))}
          </pre>
        </div>
      </main>
    </>
  );
}
