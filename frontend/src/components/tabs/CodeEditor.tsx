import { Box } from '@chakra-ui/react'
import config from '../../config'

function CodeEditor() {
  // Construct the code-server URL
  const codeServerUrl = config.apiBaseUrl 
    ? `${config.apiBaseUrl.replace('/api', '')}/code/`
    : window.location.protocol === 'https:' 
      ? 'https://' + window.location.host + '/code/'
      : 'http://' + window.location.host + '/code/'

  return (
    <Box h="100%" w="100%" position="relative">
      <iframe
        src={codeServerUrl}
        style={{
          width: '100%',
          height: '100%',
          border: 'none',
          position: 'absolute',
          top: 0,
          left: 0,
        }}
        title="VS Code Editor"
        allow="clipboard-read; clipboard-write"
      />
    </Box>
  )
}

export default CodeEditor
