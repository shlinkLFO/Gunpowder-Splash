import { Box, Flex } from '@chakra-ui/react'
import { useState } from 'react'
import Sidebar from './components/Sidebar'
import MainContent from './components/MainContent'

function App() {
  const [selectedFile, setSelectedFile] = useState<string | undefined>()

  return (
    <Flex h="100vh" bg="midnight.900">
      <Sidebar onFileSelect={setSelectedFile} selectedFile={selectedFile} />
      <Box flex="1" overflow="hidden">
        <MainContent selectedFile={selectedFile} />
      </Box>
    </Flex>
  )
}

export default App
