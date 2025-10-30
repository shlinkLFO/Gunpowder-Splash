import { useState, useEffect } from 'react'
import { Box, Button, Text, HStack, VStack, Textarea, createToaster } from '@chakra-ui/react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import Editor from '@monaco-editor/react'

const toaster = createToaster({
  placement: 'top',
  duration: 3000,
})

interface NotebookCell {
  cell_type: 'code' | 'markdown'
  source: string | string[]
  metadata?: Record<string, any>
  outputs?: any[]
  id?: string  // Stable UUID for tracking execution results
}

interface NotebookData {
  cells: NotebookCell[]
  metadata?: Record<string, any>
  nbformat?: number
  nbformat_minor?: number
}

interface CellExecutionResult {
  success: boolean
  output?: string
  error?: string
  outputs?: any[]
}

interface InlineNotebookProps {
  filepath: string
}

// Generate unique session ID per browser tab
const generateSessionId = () => {
  const storedId = sessionStorage.getItem('gunpowder-splash-session-id')
  if (storedId) return storedId
  
  const newId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  sessionStorage.setItem('gunpowder-splash-session-id', newId)
  return newId
}

// Generate stable UUID for cells
const generateCellId = () => `cell-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

export default function InlineNotebook({ filepath }: InlineNotebookProps) {
  const [notebook, setNotebook] = useState<NotebookData | null>(null)
  const [cellResults, setCellResults] = useState<Map<string, CellExecutionResult>>(new Map())
  const [executingCells, setExecutingCells] = useState<Set<string>>(new Set())
  const [editingCells, setEditingCells] = useState<Set<string>>(new Set())
  const [hoveredInsertIndex, setHoveredInsertIndex] = useState<number | null>(null)
  const [sessionId] = useState(generateSessionId())

  useEffect(() => {
    if (filepath && filepath.endsWith('.ipynb')) {
      loadNotebook()
    }
  }, [filepath])

  const loadNotebook = async () => {
    try {
      const response = await axios.post('/api/notebooks/parse', {
        filepath
      })
      
      if (response.data.success) {
        // Ensure all cells have stable IDs
        const cellsWithIds = response.data.cells.map((cell: NotebookCell) => ({
          ...cell,
          id: cell.id || generateCellId()
        }))
        
        setNotebook({
          ...response.data,
          cells: cellsWithIds
        })
        setCellResults(new Map())
      }
    } catch (error: any) {
      toaster.error({
        title: 'Error loading notebook',
        description: error.response?.data?.detail || error.message,
      })
    }
  }

  const saveNotebook = async () => {
    if (!notebook) return
    
    try {
      const notebookContent = JSON.stringify({
        cells: notebook.cells,
        metadata: notebook.metadata || {},
        nbformat: notebook.nbformat || 4,
        nbformat_minor: notebook.nbformat_minor || 5
      }, null, 2)
      
      await axios.put(`/api/files/${filepath}`, { content: notebookContent })
      toaster.success({
        title: 'Notebook saved',
      })
    } catch (error: any) {
      toaster.error({
        title: 'Error saving notebook',
        description: error.response?.data?.detail || error.message,
      })
    }
  }

  const executeCell = async (cell: NotebookCell, index: number) => {
    if (cell.cell_type !== 'code' || !cell.id) return
    
    setExecutingCells(prev => new Set(prev).add(cell.id!))
    
    try {
      const response = await axios.post('/api/notebooks/execute-cell', {
        cell,
        cell_index: index,
        filepath,
        session_id: sessionId
      })
      
      setCellResults(prev => {
        const newMap = new Map(prev)
        newMap.set(cell.id!, response.data)
        return newMap
      })
    } catch (error: any) {
      toaster.error({
        title: `Error executing cell ${index + 1}`,
        description: error.response?.data?.detail || error.message,
      })
    } finally {
      setExecutingCells(prev => {
        const newSet = new Set(prev)
        newSet.delete(cell.id!)
        return newSet
      })
    }
  }

  const insertCell = (index: number, cellType: 'code' | 'markdown') => {
    if (!notebook) return
    
    const cellId = generateCellId()
    const newCell: NotebookCell = {
      cell_type: cellType,
      source: '',
      metadata: {},
      outputs: cellType === 'code' ? [] : undefined,
      id: cellId
    }
    
    const updatedCells = [...notebook.cells]
    updatedCells.splice(index, 0, newCell)
    
    setNotebook({ ...notebook, cells: updatedCells })
    setEditingCells(prev => new Set(prev).add(cellId))
    setHoveredInsertIndex(null)
    
    toaster.create({
      title: `${cellType === 'code' ? 'Code' : 'Markdown'} cell inserted`,
      type: 'success',
    })
  }

  const updateCellSource = (index: number, newSource: string) => {
    if (!notebook) return
    
    const updatedCells = [...notebook.cells]
    updatedCells[index] = {
      ...updatedCells[index],
      source: newSource
    }
    
    setNotebook({ ...notebook, cells: updatedCells })
  }

  const deleteCell = (index: number) => {
    if (!notebook) return
    
    const cellToDelete = notebook.cells[index]
    const updatedCells = notebook.cells.filter((_, i) => i !== index)
    setNotebook({ ...notebook, cells: updatedCells })
    
    // Remove execution results for the deleted cell
    if (cellToDelete.id) {
      setCellResults(prev => {
        const newMap = new Map(prev)
        newMap.delete(cellToDelete.id!)
        return newMap
      })
      
      setEditingCells(prev => {
        const newSet = new Set(prev)
        newSet.delete(cellToDelete.id!)
        return newSet
      })
    }
    
    toaster.create({
      title: 'Cell deleted',
      type: 'info',
    })
  }

  const getCellSource = (cell: NotebookCell): string => {
    if (Array.isArray(cell.source)) {
      return cell.source.join('')
    }
    return cell.source
  }

  const toggleEditCell = (cellId: string) => {
    setEditingCells(prev => {
      const newSet = new Set(prev)
      if (newSet.has(cellId)) {
        newSet.delete(cellId)
      } else {
        newSet.add(cellId)
      }
      return newSet
    })
  }

  const renderCellOutput = (result: CellExecutionResult) => {
    if (!result) return null

    if (result.error) {
      return (
        <Box bg="rgba(255, 0, 0, 0.1)" p={3} borderRadius="md" mt={2}>
          <Text fontSize="xs" fontFamily="monospace" color="red.300" whiteSpace="pre-wrap">
            {result.error}
          </Text>
        </Box>
      )
    }

    if (result.output) {
      return (
        <Box bg="rgba(27, 16, 42, 0.8)" p={3} borderRadius="md" mt={2}>
          <Text fontSize="xs" fontFamily="monospace" color="midnight.400" whiteSpace="pre-wrap">
            {result.output}
          </Text>
        </Box>
      )
    }

    return null
  }

  if (!notebook) {
    return (
      <VStack h="100%" justify="center" gap={4}>
        <Text fontSize="lg" color="midnight.400">
          Loading notebook...
        </Text>
      </VStack>
    )
  }

  return (
    <Box h="100%">
      <VStack h="100%" align="stretch" gap={4}>
        <HStack justify="space-between">
          <Text fontSize="lg" color="midnight.400" fontWeight="bold">
            {filepath}
          </Text>
          <HStack gap={2}>
            <Button size="sm" onClick={saveNotebook}>
              💾 Save Notebook
            </Button>
            <Button 
              size="sm" 
              variant="ghost"
              onClick={() => insertCell(notebook.cells.length, 'code')}
            >
              + Code Cell
            </Button>
            <Button 
              size="sm" 
              variant="ghost"
              onClick={() => insertCell(notebook.cells.length, 'markdown')}
            >
              + Markdown Cell
            </Button>
          </HStack>
        </HStack>

        <Box flex="1" overflowY="auto">
          {notebook.cells.length === 0 ? (
            <VStack h="100%" justify="center" gap={4} p={8}>
              <Text fontSize="2xl" color="midnight.400" fontWeight="bold">
                Empty Notebook
              </Text>
              <Text fontSize="md" color="midnight.400" textAlign="center">
                This notebook has no cells yet. Add your first cell to get started!
              </Text>
              <HStack gap={4}>
                <Button 
                  size="lg" 
                  colorScheme="purple"
                  onClick={() => insertCell(0, 'code')}
                >
                  + Add Code Cell
                </Button>
                <Button 
                  size="lg" 
                  variant="outline"
                  onClick={() => insertCell(0, 'markdown')}
                >
                  + Add Markdown Cell
                </Button>
              </HStack>
            </VStack>
          ) : (
          <VStack align="stretch" gap={0}>
            {/* Insert button before first cell */}
            <Box
              h="4px"
              position="relative"
              onMouseEnter={() => setHoveredInsertIndex(0)}
              onMouseLeave={() => setHoveredInsertIndex(null)}
              mb={2}
            >
              {hoveredInsertIndex === 0 && (
                <HStack
                  position="absolute"
                  top="50%"
                  left="50%"
                  transform="translate(-50%, -50%)"
                  bg="midnight.800"
                  borderRadius="md"
                  p={1}
                  gap={2}
                  border="1px solid"
                  borderColor="midnight.600"
                  zIndex={10}
                >
                  <Button
                    size="xs"
                    onClick={() => insertCell(0, 'markdown')}
                    variant="ghost"
                  >
                    Markdown
                  </Button>
                  <Button
                    size="xs"
                    onClick={() => insertCell(0, 'code')}
                    variant="ghost"
                  >
                    Code
                  </Button>
                </HStack>
              )}
              {hoveredInsertIndex === 0 && (
                <Box h="2px" bg="midnight.500" />
              )}
            </Box>

            {notebook.cells.map((cell, index) => {
              const cellId = cell.id || generateCellId()
              return (
              <Box key={cellId}>
                <Box
                  border="1px solid"
                  borderColor={cell.cell_type === 'code' ? 'blue.700' : 'purple.700'}
                  borderRadius="md"
                  bg="rgba(27, 16, 42, 0.4)"
                  p={3}
                  mb={2}
                >
                  <HStack justify="space-between" mb={2}>
                    <HStack gap={2}>
                      <Text fontSize="xs" color="midnight.500" fontWeight="bold">
                        {cell.cell_type === 'code' ? '▶ Code' : '📝 Markdown'} Cell {index + 1}
                      </Text>
                    </HStack>
                    <HStack gap={1}>
                      {cell.cell_type === 'code' && (
                        <Button
                          size="xs"
                          colorScheme="green"
                          onClick={() => executeCell(cell, index)}
                          loading={executingCells.has(cellId)}
                        >
                          ▶ Run
                        </Button>
                      )}
                      <Button
                        size="xs"
                        variant="ghost"
                        onClick={() => toggleEditCell(cellId)}
                      >
                        {editingCells.has(cellId) ? '👁 View' : '✏️ Edit'}
                      </Button>
                      <Button
                        size="xs"
                        variant="ghost"
                        colorScheme="red"
                        onClick={() => deleteCell(index)}
                      >
                        🗑
                      </Button>
                    </HStack>
                  </HStack>

                  {/* Cell Content */}
                  {editingCells.has(cellId) ? (
                    cell.cell_type === 'code' ? (
                      <Box border="1px solid" borderColor="midnight.700" borderRadius="md" overflow="hidden">
                        <Editor
                          height="200px"
                          language="python"
                          value={getCellSource(cell)}
                          onChange={(value) => updateCellSource(index, value || '')}
                          theme="vs-dark"
                          options={{
                            minimap: { enabled: false },
                            fontSize: 13,
                            lineNumbers: 'on',
                            scrollBeyondLastLine: false,
                            automaticLayout: true,
                          }}
                        />
                      </Box>
                    ) : (
                      <Textarea
                        value={getCellSource(cell)}
                        onChange={(e) => updateCellSource(index, e.target.value)}
                        minH="100px"
                        fontSize="sm"
                        fontFamily="monospace"
                        bg="rgba(27, 16, 42, 0.8)"
                        borderColor="midnight.700"
                      />
                    )
                  ) : (
                    <Box>
                      {cell.cell_type === 'markdown' ? (
                        <Box
                          p={3}
                          borderRadius="md"
                          bg="rgba(45, 27, 71, 0.3)"
                          color="midnight.300"
                          fontSize="sm"
                          css={{
                            '& h1': { fontSize: '1.5em', fontWeight: 'bold', marginBottom: '0.5em' },
                            '& h2': { fontSize: '1.3em', fontWeight: 'bold', marginBottom: '0.5em' },
                            '& h3': { fontSize: '1.1em', fontWeight: 'bold', marginBottom: '0.5em' },
                            '& p': { marginBottom: '0.5em' },
                            '& code': { backgroundColor: 'rgba(78, 42, 132, 0.3)', padding: '2px 6px', borderRadius: '3px' },
                            '& pre': { backgroundColor: 'rgba(27, 16, 42, 0.8)', padding: '1em', borderRadius: '6px', overflowX: 'auto' },
                            '& ul, & ol': { marginLeft: '1.5em', marginBottom: '0.5em' },
                          }}
                        >
                          <ReactMarkdown>{getCellSource(cell)}</ReactMarkdown>
                        </Box>
                      ) : (
                        <Box
                          p={3}
                          borderRadius="md"
                          bg="rgba(27, 16, 42, 0.8)"
                          fontFamily="monospace"
                          fontSize="sm"
                          color="midnight.300"
                          whiteSpace="pre-wrap"
                        >
                          {getCellSource(cell)}
                        </Box>
                      )}
                    </Box>
                  )}

                  {/* Cell Output for Code Cells */}
                  {cell.cell_type === 'code' && cellResults.get(cellId) && renderCellOutput(cellResults.get(cellId)!)}
                </Box>

                {/* Insert button between cells */}
                <Box
                  h="8px"
                  position="relative"
                  onMouseEnter={() => setHoveredInsertIndex(index + 1)}
                  onMouseLeave={() => setHoveredInsertIndex(null)}
                  mb={2}
                >
                  {hoveredInsertIndex === index + 1 && (
                    <>
                      <Box h="2px" bg="midnight.500" />
                      <HStack
                        position="absolute"
                        top="50%"
                        left="50%"
                        transform="translate(-50%, -50%)"
                        bg="midnight.800"
                        borderRadius="md"
                        p={1}
                        gap={2}
                        border="1px solid"
                        borderColor="midnight.600"
                        zIndex={10}
                      >
                        <Button
                          size="xs"
                          onClick={() => insertCell(index + 1, 'markdown')}
                          variant="ghost"
                        >
                          Markdown
                        </Button>
                        <Button
                          size="xs"
                          onClick={() => insertCell(index + 1, 'code')}
                          variant="ghost"
                        >
                          Code
                        </Button>
                      </HStack>
                    </>
                  )}
                </Box>
              </Box>
            )
          })}
          </VStack>
          )}
        </Box>
      </VStack>
    </Box>
  )
}
