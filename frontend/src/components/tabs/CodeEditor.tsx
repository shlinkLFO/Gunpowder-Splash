import { Box, Text, Spinner, VStack, Button } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import axios from '../../lib/axios'

function CodeEditor() {
  const [status, setStatus] = useState<'loading' | 'starting' | 'ready' | 'error'>('loading')
  const [errorMessage, setErrorMessage] = useState<string>('')
  const [codeServerUrl, setCodeServerUrl] = useState<string>('')

  useEffect(() => {
    startCodeServer()
  }, [])

  const startCodeServer = async () => {
    try {
      setStatus('starting')
      
      // Start or access user's code-server instance
      const response = await axios.post('/v1/code-server/start')
      
      // Construct the URL to the user's code-server
      const baseUrl = window.location.origin
      const url = `${baseUrl}${response.data.url}`
      
      setCodeServerUrl(url)
      setStatus('ready')
    } catch (error: any) {
      console.error('Failed to start code-server:', error)
      setErrorMessage(error.response?.data?.detail || error.message || 'Failed to start VS Code')
      setStatus('error')
    }
  }

  if (status === 'loading' || status === 'starting') {
    return (
      <VStack h="100%" justify="center" gap={4}>
        <Spinner size="xl" color="blue.500" />
        <Text color="gray.400">
          {status === 'loading' ? 'Initializing...' : 'Starting your VS Code workspace...'}
        </Text>
        <Text fontSize="sm" color="gray.500">
          This may take a few seconds
        </Text>
      </VStack>
    )
  }

  if (status === 'error') {
    return (
      <VStack h="100%" justify="center" gap={4}>
        <Text color="red.400" fontSize="lg" fontWeight="bold">
          Failed to Start VS Code
        </Text>
        <Text color="gray.400" fontSize="sm">
          {errorMessage}
        </Text>
        <Button onClick={startCodeServer} colorScheme="blue">
          Try Again
        </Button>
      </VStack>
    )
  }

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
