import { Box, Button, VStack, HStack, Text, Code, Spinner, Heading, createToaster } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import axios from '../../lib/axios'
import Editor from '@monaco-editor/react'

interface NotebookCell {
  cell_type: 'code' | 'markdown' | 'raw'
  source: string[] | string
  metadata?: any
  outputs?: any[]
  execution_count?: number | null
}

interface NotebookData {
  cells: NotebookCell[]
  metadata: any
  nbformat: number
  nbformat_minor: number
}

interface CellExecutionResult {
  success: boolean
  cell_type: string
  cell_index: number
  source?: string
  content?: string
  outputs?: any[]
  error?: string
  dataframes?: Record<string, any>
}

interface NotebookProps {
  selectedFile?: string
}

const toaster = createToaster({
  placement: 'top',
  duration: 3000,
})

// Generate unique session ID per browser tab
const generateSessionId = () => {
  const storedId = sessionStorage.getItem('gunpowder-splash-session-id')
  if (storedId) return storedId
  
  const newId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  sessionStorage.setItem('gunpowder-splash-session-id', newId)
  return newId
}

export default function Notebook({ selectedFile }: NotebookProps) {
  const [notebook, setNotebook] = useState<NotebookData | null>(null)
  const [cellResults, setCellResults] = useState<Map<number, CellExecutionResult>>(new Map())
  const [executingCells, setExecutingCells] = useState<Set<number>>(new Set())
  const [loading, setLoading] = useState(false)
  const [editingCell, setEditingCell] = useState<number | null>(null)
  const [editedSource, setEditedSource] = useState<string>('')
  const [sessionId] = useState(generateSessionId())

  useEffect(() => {
    if (selectedFile && selectedFile.endsWith('.ipynb')) {
      loadNotebook()
    }
  }, [selectedFile])

  const loadNotebook = async () => {
    if (!selectedFile) return
    
    setLoading(true)
    try {
      const response = await axios.post('/api/notebooks/parse', {
        filepath: selectedFile
      })
      
      if (response.data.success) {
        setNotebook(response.data)
        setCellResults(new Map())
        toaster.success({
          title: 'Notebook loaded',
        })
      }
    } catch (error: any) {
      toaster.error({
        title: 'Error loading notebook',
        description: error.response?.data?.detail || error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const executeCell = async (cell: NotebookCell, index: number) => {
    if (!selectedFile) return
    setExecutingCells(prev => new Set(prev).add(index))
    
    try {
      const response = await axios.post('/api/notebooks/execute-cell', {
        cell,
        cell_index: index,
        filepath: selectedFile,
        session_id: sessionId
      })
      
      setCellResults(prev => {
        const newMap = new Map(prev)
        newMap.set(index, response.data)
        return newMap
      })
      
      if (response.data.success) {
        toaster.success({
          title: `Cell ${index + 1} executed`,
        })
      }
    } catch (error: any) {
      toaster.error({
        title: `Error executing cell ${index + 1}`,
        description: error.response?.data?.detail || error.message,
      })
    } finally {
      setExecutingCells(prev => {
        const newSet = new Set(prev)
        newSet.delete(index)
        return newSet
      })
    }
  }

  const executeAllCells = async () => {
    if (!notebook || !selectedFile) return
    
    setLoading(true)
    try {
      const response = await axios.post('/api/notebooks/execute-all', {
        cells: notebook.cells,
        filepath: selectedFile,
        session_id: sessionId
      })
      
      const newResults = new Map<number, CellExecutionResult>()
      response.data.results.forEach((result: CellExecutionResult, index: number) => {
        newResults.set(index, result)
      })
      setCellResults(newResults)
      
      toaster.success({
        title: 'All cells executed',
      })
    } catch (error: any) {
      toaster.error({
        title: 'Error executing cells',
        description: error.response?.data?.detail || error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const resetContext = async () => {
    if (!selectedFile) return
    try {
      await axios.post('/api/notebooks/reset', {
        filepath: selectedFile,
        session_id: sessionId
      })
      setCellResults(new Map())
      toaster.success({
        title: 'Notebook context reset',
      })
    } catch (error: any) {
      toaster.error({
        title: 'Error resetting context',
        description: error.response?.data?.detail || error.message,
      })
    }
  }

  const getCellSource = (cell: NotebookCell): string => {
    if (Array.isArray(cell.source)) {
      return cell.source.join('')
    }
    return cell.source
  }

  const startEditingCell = (index: number) => {
    if (!notebook) return
    const cell = notebook.cells[index]
    setEditingCell(index)
    setEditedSource(getCellSource(cell))
  }

  const saveEditedCell = () => {
    if (editingCell === null || !notebook) return
    
    const updatedCells = [...notebook.cells]
    updatedCells[editingCell] = {
      ...updatedCells[editingCell],
      source: editedSource
    }
    
    setNotebook({ ...notebook, cells: updatedCells })
    setEditingCell(null)
    setEditedSource('')
    
    toaster.create({
      title: 'Cell updated',
      description: 'Changes are local only. Save the notebook file to persist.',
      type: 'info',
    })
  }

  const cancelEdit = () => {
    setEditingCell(null)
    setEditedSource('')
  }

  const renderMarkdownCell = (cell: NotebookCell, index: number) => {
    const source = getCellSource(cell)
    const isEditing = editingCell === index
    
    return (
      <Box
        key={index}
        p={4}
        borderWidth="1px"
        borderColor="midnight.700"
        borderRadius="md"
        bg="midnight.800"
      >
        <HStack justify="space-between" mb={2}>
          <Text fontSize="sm" color="midnight.500" fontWeight="600">
            Markdown Cell [{index + 1}]
          </Text>
          {!isEditing && (
            <Button size="sm" colorScheme="purple" onClick={() => startEditingCell(index)}>
              Edit
            </Button>
          )}
        </HStack>
        
        {isEditing ? (
          <VStack align="stretch" gap={2}>
            <Editor
              height="200px"
              language="markdown"
              theme="vs-dark"
              value={editedSource}
              onChange={(value) => setEditedSource(value || '')}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
              }}
            />
            <HStack>
              <Button size="sm" colorScheme="green" onClick={saveEditedCell}>
                Save
              </Button>
              <Button size="sm" variant="ghost" onClick={cancelEdit}>
                Cancel
              </Button>
            </HStack>
          </VStack>
        ) : (
          <Box
            p={3}
            bg="midnight.900"
            borderRadius="md"
            color="midnight.400"
            whiteSpace="pre-wrap"
            fontFamily="body"
          >
            {source}
          </Box>
        )}
      </Box>
    )
  }

  const renderCodeCell = (cell: NotebookCell, index: number) => {
    const source = getCellSource(cell)
    const result = cellResults.get(index)
    const isExecuting = executingCells.has(index)
    const isEditing = editingCell === index
    
    return (
      <Box
        key={index}
        borderWidth="1px"
        borderColor="midnight.700"
        borderRadius="md"
        bg="midnight.800"
        overflow="hidden"
      >
        <HStack justify="space-between" p={3} bg="midnight.900">
          <Text fontSize="sm" color="midnight.500" fontWeight="600">
            Code Cell [{index + 1}]
          </Text>
          <HStack gap={2}>
            {!isEditing && (
              <>
                <Button
                  size="sm"
                  colorScheme="green"
                  onClick={() => executeCell(cell, index)}
                  loading={isExecuting}
                  loadingText="Running"
                >
                  ▶ Run
                </Button>
                <Button size="sm" variant="ghost" onClick={() => startEditingCell(index)}>
                  Edit
                </Button>
              </>
            )}
          </HStack>
        </HStack>
        
        {isEditing ? (
          <Box p={3}>
            <Editor
              height="200px"
              language="python"
              theme="vs-dark"
              value={editedSource}
              onChange={(value) => setEditedSource(value || '')}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
              }}
            />
            <HStack mt={2}>
              <Button size="sm" colorScheme="green" onClick={saveEditedCell}>
                Save
              </Button>
              <Button size="sm" variant="ghost" onClick={cancelEdit}>
                Cancel
              </Button>
            </HStack>
          </Box>
        ) : (
          <Box p={3}>
            <Code
              display="block"
              whiteSpace="pre"
              p={3}
              bg="midnight.900"
              color="midnight.400"
              borderRadius="md"
              fontFamily="monospace"
              fontSize="sm"
            >
              {source}
            </Code>
          </Box>
        )}
        
        {result && (
          <Box p={3} bg="midnight.900" borderTopWidth="1px" borderColor="midnight.700">
            {result.outputs && result.outputs.length > 0 && (
              <Box mb={2}>
                <Text fontSize="xs" color="midnight.500" mb={1}>Output:</Text>
                {result.outputs.map((output: any, i: number) => (
                  <Code
                    key={i}
                    display="block"
                    whiteSpace="pre-wrap"
                    p={2}
                    bg="black"
                    color="green.300"
                    borderRadius="md"
                    fontFamily="monospace"
                    fontSize="sm"
                  >
                    {output.text}
                  </Code>
                ))}
              </Box>
            )}
            
            {result.error && (
              <Box>
                <Text fontSize="xs" color="red.400" mb={1}>Error:</Text>
                <Code
                  display="block"
                  whiteSpace="pre-wrap"
                  p={2}
                  bg="black"
                  color="red.300"
                  borderRadius="md"
                  fontFamily="monospace"
                  fontSize="sm"
                >
                  {result.error}
                </Code>
              </Box>
            )}
            
            {result.dataframes && Object.keys(result.dataframes).length > 0 && (
              <Box mt={2}>
                <Text fontSize="xs" color="midnight.500" mb={1}>DataFrames:</Text>
                {Object.entries(result.dataframes).map(([name, df]: [string, any]) => (
                  <Text key={name} fontSize="sm" color="midnight.400">
                    {name}: {df.shape[0]} rows × {df.shape[1]} columns
                  </Text>
                ))}
              </Box>
            )}
          </Box>
        )}
      </Box>
    )
  }

  if (!selectedFile || !selectedFile.endsWith('.ipynb')) {
    return (
      <Box p={8} textAlign="center">
        <Text color="midnight.500" fontSize="lg">
          Select a .ipynb file to view and execute Jupyter notebooks
        </Text>
      </Box>
    )
  }

  if (loading && !notebook) {
    return (
      <Box p={8} textAlign="center">
        <Spinner size="xl" color="midnight.500" />
        <Text color="midnight.500" mt={4}>Loading notebook...</Text>
      </Box>
    )
  }

  if (!notebook) {
    return (
      <Box p={8} textAlign="center">
        <Text color="midnight.500" fontSize="lg" mb={4}>
          Notebook not loaded
        </Text>
        <Button colorScheme="purple" onClick={loadNotebook}>
          Load Notebook
        </Button>
      </Box>
    )
  }

  return (
    <Box h="100%" display="flex" flexDirection="column" bg="midnight.900">
      <Box
        p={4}
        borderBottomWidth="1px"
        borderColor="midnight.700"
        bg="midnight.800"
      >
        <HStack justify="space-between">
          <Heading size="md" color="midnight.400">
            {selectedFile}
          </Heading>
          <HStack gap={2}>
            <Button
              size="sm"
              colorScheme="green"
              onClick={executeAllCells}
              loading={loading}
            >
              ▶▶ Run All
            </Button>
            <Button
              size="sm"
              colorScheme="orange"
              onClick={resetContext}
            >
              Reset
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={loadNotebook}
            >
              Reload
            </Button>
          </HStack>
        </HStack>
        <Text fontSize="sm" color="midnight.500" mt={2}>
          {notebook.cells.length} cells | nbformat {notebook.nbformat}.{notebook.nbformat_minor}
        </Text>
      </Box>
      
      <Box flex="1" overflowY="auto" p={4}>
        <VStack align="stretch" gap={4}>
          {notebook.cells.map((cell, index) => {
            if (cell.cell_type === 'markdown') {
              return renderMarkdownCell(cell, index)
            } else if (cell.cell_type === 'code') {
              return renderCodeCell(cell, index)
            }
            return null
          })}
        </VStack>
      </Box>
    </Box>
  )
}
