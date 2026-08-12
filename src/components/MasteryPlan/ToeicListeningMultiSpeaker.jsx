import SharedListeningDiagnostic from './SharedListeningDiagnostic.jsx';

const ToeicListeningMultiSpeaker = ({ onRemediationCreated }) => (
  <SharedListeningDiagnostic
    endpoint="/api/diagnostic/toeic-listening-multi-speaker"
    moduleId="multi-speaker"
    onRemediationCreated={onRemediationCreated}
  />
);

export default ToeicListeningMultiSpeaker;
