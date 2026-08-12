import SharedListeningDiagnostic from './SharedListeningDiagnostic.jsx';

const ToeicListeningConversationsTalks = ({ onRemediationCreated }) => (
  <SharedListeningDiagnostic
    endpoint="/api/diagnostic/toeic-listening-conversations-talks"
    moduleId="conversations-talks"
    onRemediationCreated={onRemediationCreated}
  />
);

export default ToeicListeningConversationsTalks;
