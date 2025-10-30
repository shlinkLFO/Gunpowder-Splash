import { Box, VStack, Heading, Text, Button, Input, HStack } from '@chakra-ui/react'
import { useState } from 'react'
import axios from 'axios'
import FileTree from './FileTree'

interface SidebarProps {
  onFileSelect: (path: string) => void
  selectedFile?: string
}

function Sidebar({ onFileSelect, selectedFile }: SidebarProps) {
  const [newFileName, setNewFileName] = useState('')
  const [newFolderName, setNewFolderName] = useState('')
  const [showNewFile, setShowNewFile] = useState(false)
  const [showNewFolder, setShowNewFolder] = useState(false)
  const [isFileTreeCollapsed, setIsFileTreeCollapsed] = useState(false)

  const createFile = async () => {
    if (!newFileName.trim()) return
    
    try {
      await axios.post('/api/files/create', {
        path: newFileName,
        content: ''
      })
      setNewFileName('')
      setShowNewFile(false)
      window.location.reload()
    } catch (error) {
      console.error('Error creating file:', error)
      alert('Error creating file')
    }
  }

  const createFolder = async () => {
    if (!newFolderName.trim()) return
    
    try {
      await axios.post('/api/files/folder', {
        path: newFolderName
      })
      setNewFolderName('')
      setShowNewFolder(false)
      window.location.reload()
    } catch (error) {
      console.error('Error creating folder:', error)
      alert('Error creating folder')
    }
  }

  return (
    <Box
      w="300px"
      bg="linear-gradient(180deg, #1B102A 0%, #2D1B47 100%)"
      borderRight="1px solid"
      borderColor="midnight.700"
      p={4}
      overflowY="auto"
    >
      <VStack align="stretch" gap={4}>
        <Heading size="md" color="midnight.400">
          Collaborative IDE
        </Heading>
        
        <VStack align="stretch" gap={2}>
          <HStack>
            <Button size="sm" flex="1" onClick={() => setShowNewFile(!showNewFile)}>
              + File
            </Button>
            <Button size="sm" flex="1" onClick={() => setShowNewFolder(!showNewFolder)}>
              + Folder
            </Button>
          </HStack>

          {showNewFile && (
            <VStack align="stretch" gap={2}>
              <Input
                size="sm"
                placeholder="filename.py"
                value={newFileName}
                onChange={(e) => setNewFileName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && createFile()}
              />
              <HStack>
                <Button size="sm" flex="1" onClick={createFile}>Create</Button>
                <Button size="sm" flex="1" variant="ghost" onClick={() => setShowNewFile(false)}>Cancel</Button>
              </HStack>
            </VStack>
          )}

          {showNewFolder && (
            <VStack align="stretch" gap={2}>
              <Input
                size="sm"
                placeholder="folder_name"
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && createFolder()}
              />
              <HStack>
                <Button size="sm" flex="1" onClick={createFolder}>Create</Button>
                <Button size="sm" flex="1" variant="ghost" onClick={() => setShowNewFolder(false)}>Cancel</Button>
              </HStack>
            </VStack>
          )}
        </VStack>

        <Box>
          <HStack justify="space-between" mb={2}>
            <Text fontSize="sm" fontWeight="bold" color="midnight.400">
              Workspace Files
            </Text>
            <Button
              size="xs"
              variant="ghost"
              onClick={() => setIsFileTreeCollapsed(!isFileTreeCollapsed)}
              color="midnight.400"
              p={1}
              minW="auto"
            >
              {isFileTreeCollapsed ? '▸' : '▾'}
            </Button>
          </HStack>
          <FileTree 
            onFileSelect={onFileSelect} 
            selectedFile={selectedFile}
            isCollapsed={isFileTreeCollapsed}
          />
        </Box>
      </VStack>
    </Box>
  )
}

export default Sidebar
