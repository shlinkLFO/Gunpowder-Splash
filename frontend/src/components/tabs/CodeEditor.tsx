import { useState, useEffect } from 'react'
import { Box, Button, Text, HStack, VStack } from '@chakra-ui/react'
import Editor from '@monaco-editor/react'
import axios from 'axios'
import InlineNotebook from './InlineNotebook'
import RainbowCSV from './RainbowCSV'

interface CodeEditorProps {
  selectedFile?: string
}

function CodeEditor({ selectedFile }: CodeEditorProps) {
  const [code, setCode] = useState('')
  const [output, setOutput] = useState('')
  const [isRunning, setIsRunning] = useState(false)
  const [language, setLanguage] = useState('python')

  useEffect(() => {
    if (selectedFile) {
      loadFile(selectedFile)
    }
  }, [selectedFile])

  const loadFile = async (path: string) => {
    try {
      // Don't load .ipynb, .csv, .xlsx, .xls files as text - they have special viewers
      const ext = path.split('.').pop()?.toLowerCase()
      if (ext === 'ipynb' || ext === 'csv' || ext === 'xlsx' || ext === 'xls') {
        setLanguage('json')
        setCode('')
        return
      }
      
      const response = await axios.get(`/api/files/${path}`)
      setCode(response.data.content)
      
      if (ext === 'py') setLanguage('python')
      else if (ext === 'js') setLanguage('javascript')
      else if (ext === 'ts') setLanguage('typescript')
      else if (ext === 'jsx' || ext === 'tsx') setLanguage('typescript')
      else if (ext === 'json') setLanguage('json')
      else if (ext === 'md') setLanguage('markdown')
      else if (ext === 'html') setLanguage('html')
      else if (ext === 'css') setLanguage('css')
      else if (ext === 'cpp' || ext === 'cc' || ext === 'cxx') setLanguage('cpp')
      else if (ext === 'cs') setLanguage('csharp')
      else if (ext === 'php') setLanguage('php')
      else if (ext === 'txt') setLanguage('plaintext')
      else setLanguage('plaintext')
    } catch (error) {
      console.error('Error loading file:', error)
      alert('Error loading file')
    }
  }

  const saveFile = async () => {
    if (!selectedFile) {
      alert('No file selected')
      return
    }

    try {
      await axios.put(`/api/files/${selectedFile}`, { content: code })
      alert('File saved successfully')
    } catch (error) {
      console.error('Error saving file:', error)
      alert('Error saving file')
    }
  }

  const runCode = async () => {
    if (!code.trim() || language !== 'python') {
      alert('Only Python code can be executed')
      return
    }

    setIsRunning(true)
    setOutput('Running...')

    try {
      const response = await axios.post('/api/data/execute', { code })
      setOutput(response.data.output || response.data.error || 'No output')
    } catch (error: any) {
      setOutput(`Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setIsRunning(false)
    }
  }

  // Check if the file is a Jupyter notebook, CSV, or Excel
  const isNotebook = selectedFile?.endsWith('.ipynb')
  const isCSV = selectedFile?.endsWith('.csv')
  const isExcel = selectedFile?.endsWith('.xlsx') || selectedFile?.endsWith('.xls')
  const isTabularData = isCSV || isExcel

  return (
    <Box h="100%">
      {!selectedFile ? (
        <VStack h="100%" justify="center" gap={4}>
          <Text fontSize="lg" color="midnight.400">
            Select a file from the sidebar to start editing
          </Text>
          <Text fontSize="sm" color="midnight.500">
            Or create a new file using the + File button
          </Text>
        </VStack>
      ) : isNotebook ? (
        <InlineNotebook filepath={selectedFile} />
      ) : isTabularData ? (
        <RainbowCSV filepath={selectedFile} />
      ) : (
        <VStack h="100%" align="stretch" gap={4}>
          <HStack justify="space-between">
            <Text fontSize="lg" color="midnight.400" fontWeight="bold">
              {selectedFile}
            </Text>
            <HStack gap={2}>
              <Button size="sm" onClick={saveFile}>
                💾 Save
              </Button>
              {language === 'python' && (
                <Button 
                  size="sm" 
                  onClick={runCode} 
                  disabled={isRunning}
                  colorScheme="green"
                >
                  ▶ Run
                </Button>
              )}
              <Button size="sm" variant="ghost" onClick={() => setCode('')}>
                🗑 Clear
              </Button>
            </HStack>
          </HStack>

          <Box 
            flex="1" 
            border="1px solid" 
            borderColor="midnight.700" 
            borderRadius="md"
            overflow="hidden"
          >
            <Editor
              height="100%"
              language={language}
              value={code}
              onChange={(value) => setCode(value || '')}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                roundedSelection: false,
                scrollBeyondLastLine: false,
                readOnly: false,
                automaticLayout: true,
              }}
            />
          </Box>

          {output && (
            <Box
              h="200px"
              bg="rgba(27, 16, 42, 0.8)"
              border="1px solid"
              borderColor="midnight.700"
              borderRadius="md"
              p={4}
              overflowY="auto"
            >
              <Text fontSize="sm" fontWeight="bold" color="midnight.400" mb={2}>
                Output:
              </Text>
              <Text fontSize="sm" color="midnight.400" fontFamily="monospace" whiteSpace="pre-wrap">
                {output}
              </Text>
            </Box>
          )}
        </VStack>
      )}
    </Box>
  )
}

export default CodeEditor
