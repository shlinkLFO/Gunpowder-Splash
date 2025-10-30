import { Box, VStack, Text, HStack, Grid, GridItem, Button } from '@chakra-ui/react'

function System() {
  const systemInfo = {
    python: 'Python 3.11',
    node: 'Node.js 20',
    backend: 'FastAPI + Uvicorn',
    frontend: 'React 18 + Vite',
    database: 'In-Memory (Pandas)',
    websocket: 'Running on port 8001',
  }

  const packages = {
    backend: [
      'fastapi',
      'uvicorn',
      'pandas',
      'numpy',
      'plotly',
      'websockets',
      'python-socketio',
      'aiofiles',
      'python-multipart'
    ],
    frontend: [
      'react',
      'react-dom',
      'vite',
      'typescript',
      '@chakra-ui/react',
      '@monaco-editor/react',
      'socket.io-client',
      '@tanstack/react-query',
      'axios',
      'zustand'
    ]
  }

  return (
    <Box h="100%">
      <VStack align="stretch" gap={4} h="100%" overflowY="auto">
        <Text fontSize="lg" color="midnight.400" fontWeight="bold">
          System Information
        </Text>

        <Grid templateColumns="repeat(2, 1fr)" gap={4}>
          {Object.entries(systemInfo).map(([key, value]) => (
            <GridItem key={key}>
              <Box
                p={4}
                bg="rgba(27, 16, 42, 0.5)"
                border="1px solid"
                borderColor="midnight.700"
                borderRadius="md"
              >
                <Text fontSize="sm" color="midnight.500" textTransform="uppercase">
                  {key}
                </Text>
                <Text fontSize="md" color="midnight.400" fontWeight="bold" mt={1}>
                  {value}
                </Text>
              </Box>
            </GridItem>
          ))}
        </Grid>

        <Box
          p={4}
          bg="rgba(27, 16, 42, 0.5)"
          border="1px solid"
          borderColor="midnight.700"
          borderRadius="md"
        >
          <HStack justify="space-between" mb={3}>
            <Text fontSize="md" color="midnight.400" fontWeight="bold">
              Backend Packages
            </Text>
            <Text fontSize="sm" color="midnight.500">
              {packages.backend.length} packages
            </Text>
          </HStack>
          <Grid templateColumns="repeat(3, 1fr)" gap={2}>
            {packages.backend.map((pkg) => (
              <Box
                key={pkg}
                px={3}
                py={1}
                bg="midnight.800"
                borderRadius="md"
                fontSize="sm"
                color="midnight.400"
              >
                {pkg}
              </Box>
            ))}
          </Grid>
        </Box>

        <Box
          p={4}
          bg="rgba(27, 16, 42, 0.5)"
          border="1px solid"
          borderColor="midnight.700"
          borderRadius="md"
        >
          <HStack justify="space-between" mb={3}>
            <Text fontSize="md" color="midnight.400" fontWeight="bold">
              Frontend Packages
            </Text>
            <Text fontSize="sm" color="midnight.500">
              {packages.frontend.length} packages
            </Text>
          </HStack>
          <Grid templateColumns="repeat(3, 1fr)" gap={2}>
            {packages.frontend.map((pkg) => (
              <Box
                key={pkg}
                px={3}
                py={1}
                bg="midnight.800"
                borderRadius="md"
                fontSize="sm"
                color="midnight.400"
              >
                {pkg}
              </Box>
            ))}
          </Grid>
        </Box>

        <Box
          p={4}
          bg="rgba(27, 16, 42, 0.5)"
          border="1px solid"
          borderColor="midnight.700"
          borderRadius="md"
        >
          <Text fontSize="md" color="midnight.400" fontWeight="bold" mb={3}>
            Environment
          </Text>
          <VStack align="stretch" gap={2}>
            <HStack>
              <Text fontSize="sm" color="midnight.500" w="200px">
                Backend Server:
              </Text>
              <Text fontSize="sm" color="green.400" fontWeight="bold">
                ✓ Running (Port 8000)
              </Text>
            </HStack>
            <HStack>
              <Text fontSize="sm" color="midnight.500" w="200px">
                Frontend Server:
              </Text>
              <Text fontSize="sm" color="green.400" fontWeight="bold">
                ✓ Running (Port 5000)
              </Text>
            </HStack>
            <HStack>
              <Text fontSize="sm" color="midnight.500" w="200px">
                WebSocket Server:
              </Text>
              <Text fontSize="sm" color="green.400" fontWeight="bold">
                ✓ Running (Port 8001)
              </Text>
            </HStack>
          </VStack>
        </Box>

        <HStack gap={2}>
          <Button size="sm" flex="1" onClick={() => window.location.reload()}>
            🔄 Refresh Page
          </Button>
          <Button size="sm" flex="1" variant="ghost">
            📊 View Logs (Coming Soon)
          </Button>
        </HStack>
      </VStack>
    </Box>
  )
}

export default System
