import { useState, useEffect, useRef } from 'react'
import { Box, Button, HStack, Text, VStack, Input } from '@chakra-ui/react'
import axios from 'axios'
import * as Papa from 'papaparse'

interface RainbowCSVProps {
  filepath: string
}

const COLUMN_COLORS = [
  '#E8D9FF', '#FFB3E6', '#B3E6FF', '#B3FFD9', '#FFE6B3',
  '#D9B3FF', '#FFD9B3', '#B3FFB3', '#FFB3D9', '#D9FFB3',
]

const DEFAULT_COL_WIDTH = 200
const MIN_COL_WIDTH = 50
const ROW_INDEX_DEFAULT_WIDTH = 60
const ROW_INDEX_MIN_WIDTH = 30
const DEFAULT_ROW_HEIGHT = 40
const MIN_ROW_HEIGHT = 30

export default function RainbowCSV({ filepath }: RainbowCSVProps) {
  const [tableData, setTableData] = useState<string[][]>([])
  const [headers, setHeaders] = useState<string[]>([])
  const [columnWidths, setColumnWidths] = useState<number[]>([])
  const [rowHeights, setRowHeights] = useState<number[]>([])
  const [rowIndexWidth, setRowIndexWidth] = useState(ROW_INDEX_DEFAULT_WIDTH)
  const [isExcel, setIsExcel] = useState(false)
  const [fileType, setFileType] = useState<'csv' | 'xlsx' | 'xls'>('csv')
  const [editingCell, setEditingCell] = useState<{ row: number; col: number } | null>(null)
  const [editValue, setEditValue] = useState('')
  const [viewMode, setViewMode] = useState<'table' | 'lines'>('table')

  const resizingRef = useRef<{ colIndex: number; startX: number; startWidth: number } | null>(null)
  const resizingRowIndexRef = useRef<{ startX: number; startWidth: number } | null>(null)
  const resizingRowRef = useRef<{ rowIndex: number; startY: number; startHeight: number } | null>(null)

  useEffect(() => {
    if (filepath) {
      loadFile()
    }
  }, [filepath])

  const loadFile = async () => {
    const ext = filepath.split('.').pop()?.toLowerCase()
    
    if (ext === 'xlsx' || ext === 'xls') {
      setIsExcel(true)
      setFileType(ext as 'xlsx' | 'xls')
      await loadExcelFile()
    } else {
      setIsExcel(false)
      setFileType('csv')
      await loadCSVFile()
    }
  }

  const loadExcelFile = async () => {
    try {
      const response = await axios.get(`/api/files/parse-excel/${filepath}`)
      const data = response.data.data as string[][]
      
      if (data.length > 0) {
        setHeaders(data[0])
        setTableData(data.slice(1))
        setColumnWidths(new Array(data[0].length).fill(DEFAULT_COL_WIDTH))
        setRowHeights([])
      }
    } catch (error) {
      console.error('Error loading Excel file:', error)
      alert('Error loading Excel file')
    }
  }

  const loadCSVFile = async () => {
    try {
      const response = await axios.get(`/api/files/${filepath}`)
      const content = response.data.content
      parseCSV(content)
    } catch (error) {
      console.error('Error loading CSV:', error)
    }
  }

  const parseCSV = (content: string) => {
    if (!content || content.trim() === '') {
      setTableData([])
      setHeaders([])
      setColumnWidths([])
      return
    }

    try {
      const result = Papa.parse<string[]>(content, {
        header: false,
        skipEmptyLines: true,
        dynamicTyping: false,
      })

      if (result.errors && result.errors.length > 0) {
        console.error('CSV parsing errors:', result.errors)
      }

      const rows = result.data
      if (!rows || rows.length === 0) {
        setTableData([])
        setHeaders([])
        setColumnWidths([])
        return
      }

      setHeaders(rows[0] || [])
      setTableData(rows.slice(1) || [])
      setColumnWidths(new Array(rows[0].length).fill(DEFAULT_COL_WIDTH))
      setRowHeights([])
    } catch (error) {
      console.error('Error parsing CSV:', error)
      alert('Error parsing CSV file.')
    }
  }

  const startCellEdit = (row: number, col: number) => {
    if (row === -1) {
      setEditValue(headers[col] || '')
    } else {
      setEditValue(tableData[row]?.[col] || '')
    }
    setEditingCell({ row, col })
  }

  const finishCellEdit = () => {
    if (editingCell) {
      let updatedHeaders = [...headers]
      let updatedData = [...tableData]
      
      if (editingCell.row === -1) {
        updatedHeaders[editingCell.col] = editValue
        setHeaders(updatedHeaders)
      } else {
        if (!updatedData[editingCell.row]) {
          updatedData[editingCell.row] = []
        }
        updatedData[editingCell.row][editingCell.col] = editValue
        setTableData(updatedData)
      }
      
      // Auto-save in background (non-blocking)
      autoSave(updatedHeaders, updatedData)
    }
    // Clear edit state immediately for responsive UI
    setEditingCell(null)
    setEditValue('')
  }
  
  const autoSave = async (updatedHeaders: string[], updatedData: string[][]) => {
    try {
      const allData = [updatedHeaders, ...updatedData]

      if (isExcel) {
        if (fileType === 'xls') {
          console.error('.xls format does not support editing')
          return
        }
        
        await axios.put(`/api/files/save-excel/${filepath}`, { data: allData })
      } else {
        const csv = Papa.unparse(allData)
        await axios.put(`/api/files/${filepath}`, { content: csv })
      }
    } catch (error) {
      console.error('Error auto-saving file:', error)
    }
  }

  const handleMouseDownResize = (colIndex: number, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    resizingRef.current = {
      colIndex,
      startX: e.clientX,
      startWidth: columnWidths[colIndex] || DEFAULT_COL_WIDTH,
    }

    const handleMouseMove = (moveEvent: MouseEvent) => {
      if (resizingRef.current) {
        const diff = moveEvent.clientX - resizingRef.current.startX
        const newWidth = Math.max(MIN_COL_WIDTH, resizingRef.current.startWidth + diff)
        const newWidths = [...columnWidths]
        newWidths[resizingRef.current.colIndex] = newWidth
        setColumnWidths(newWidths)
      }
    }

    const handleMouseUp = () => {
      resizingRef.current = null
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  }

  const handleMouseDownResizeRowIndex = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    resizingRowIndexRef.current = {
      startX: e.clientX,
      startWidth: rowIndexWidth,
    }

    const handleMouseMove = (moveEvent: MouseEvent) => {
      if (resizingRowIndexRef.current) {
        const diff = moveEvent.clientX - resizingRowIndexRef.current.startX
        const newWidth = Math.max(ROW_INDEX_MIN_WIDTH, resizingRowIndexRef.current.startWidth + diff)
        setRowIndexWidth(newWidth)
      }
    }

    const handleMouseUp = () => {
      resizingRowIndexRef.current = null
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  }

  const handleMouseDownResizeRow = (rowIndex: number, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    resizingRowRef.current = {
      rowIndex,
      startY: e.clientY,
      startHeight: rowHeights[rowIndex] || DEFAULT_ROW_HEIGHT,
    }

    const handleMouseMove = (moveEvent: MouseEvent) => {
      if (resizingRowRef.current) {
        const diff = moveEvent.clientY - resizingRowRef.current.startY
        const newHeight = Math.max(MIN_ROW_HEIGHT, resizingRowRef.current.startHeight + diff)
        const newHeights = [...rowHeights]
        newHeights[resizingRowRef.current.rowIndex] = newHeight
        setRowHeights(newHeights)
      }
    }

    const handleMouseUp = () => {
      resizingRowRef.current = null
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  }

  const getColumnColor = (index: number): string => {
    return COLUMN_COLORS[index % COLUMN_COLORS.length]
  }

  if (headers.length === 0 && tableData.length === 0) {
    return (
      <VStack h="100%" justify="center" gap={4}>
        <Text fontSize="2xl" color="midnight.400" fontWeight="bold">
          Empty File
        </Text>
        <Text fontSize="md" color="midnight.400">
          This file is empty.
        </Text>
      </VStack>
    )
  }

  return (
    <VStack h="100%" align="stretch" gap={4}>
      <HStack justify="space-between">
        <Text fontSize="lg" color="midnight.400" fontWeight="bold">
          {filepath} {isExcel && `(${fileType.toUpperCase()})`}
        </Text>
        <HStack gap={2}>
          <Button
            size="sm"
            onClick={() => setViewMode(viewMode === 'table' ? 'lines' : 'table')}
            bg={viewMode === 'lines' ? 'plum.600' : 'midnight.700'}
          >
            {viewMode === 'table' ? '📄 Line View' : '📊 Table View'}
          </Button>
          <Text fontSize="sm" color="midnight.500">
            {tableData.length} rows × {headers.length} columns
          </Text>
        </HStack>
      </HStack>

      {viewMode === 'lines' ? (
        <Box
          flex="1"
          overflowX="auto"
          overflowY="auto"
          bg="midnight.900"
          borderRadius="md"
          border="1px solid"
          borderColor="midnight.700"
          fontFamily="monospace"
          fontSize="14px"
        >
          <Box p={4}>
            {/* Header row */}
            <HStack gap={0} align="flex-start" mb={1} whiteSpace="nowrap">
              <Text
                color="midnight.500"
                minW="50px"
                textAlign="right"
                pr={4}
                userSelect="none"
                fontWeight="bold"
                flexShrink={0}
              >
                1
              </Text>
              <Box whiteSpace="nowrap">
                {headers.map((header, colIndex) => (
                  <Text
                    as="span"
                    key={colIndex}
                    color={getColumnColor(colIndex)}
                    fontStyle="italic"
                  >
                    {header}
                    {colIndex < headers.length - 1 && ','}
                  </Text>
                ))}
              </Box>
            </HStack>
            
            {/* Data rows */}
            {tableData.map((row, rowIndex) => (
              <HStack key={rowIndex} gap={0} align="flex-start" mb={1} whiteSpace="nowrap">
                <Text
                  color="midnight.500"
                  minW="50px"
                  textAlign="right"
                  pr={4}
                  userSelect="none"
                  fontWeight="bold"
                  flexShrink={0}
                >
                  {rowIndex + 2}
                </Text>
                <Box whiteSpace="nowrap">
                  {row.map((cell, colIndex) => (
                    <Text
                      as="span"
                      key={colIndex}
                      color={getColumnColor(colIndex)}
                    >
                      {cell || ''}
                      {colIndex < row.length - 1 && ','}
                    </Text>
                  ))}
                </Box>
              </HStack>
            ))}
          </Box>
        </Box>
      ) : (
        <Box
          flex="1"
          overflowX="auto"
          overflowY="auto"
          bg="midnight.900"
          borderRadius="md"
          border="1px solid"
          borderColor="midnight.700"
        >
          <table
          style={{
            borderCollapse: 'collapse',
            width: '100%',
            backgroundColor: '#1B102A',
          }}
        >
          <thead
            style={{
              position: 'sticky',
              top: 0,
              backgroundColor: '#2A1940',
              zIndex: 10,
            }}
          >
            <tr>
              <th
                style={{
                  position: 'sticky',
                  left: 0,
                  backgroundColor: '#1B102A',
                  zIndex: 11,
                  width: `${rowIndexWidth}px`,
                  minWidth: `${rowIndexWidth}px`,
                  maxWidth: `${rowIndexWidth}px`,
                  borderRight: '1px solid #4E2A84',
                  borderBottom: '1px solid #4E2A84',
                  padding: '8px',
                  textAlign: 'center',
                  fontSize: '12px',
                  color: '#8B7AA8',
                }}
              >
                #
                <div
                  onMouseDown={handleMouseDownResizeRowIndex}
                  style={{
                    position: 'absolute',
                    right: 0,
                    top: 0,
                    bottom: 0,
                    width: '4px',
                    cursor: 'col-resize',
                    backgroundColor: 'transparent',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#4E2A84'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent'
                  }}
                />
              </th>
              {headers.map((header, colIndex) => (
                <th
                  key={colIndex}
                  onClick={() => startCellEdit(-1, colIndex)}
                  style={{
                    position: 'relative',
                    width: `${columnWidths[colIndex] || DEFAULT_COL_WIDTH}px`,
                    minWidth: `${columnWidths[colIndex] || DEFAULT_COL_WIDTH}px`,
                    maxWidth: `${columnWidths[colIndex] || DEFAULT_COL_WIDTH}px`,
                    borderRight: '1px solid #4E2A84',
                    borderBottom: '1px solid #4E2A84',
                    padding: '8px 12px',
                    textAlign: 'left',
                    fontSize: '14px',
                    fontWeight: 'bold',
                    color: getColumnColor(colIndex),
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}
                >
                  {editingCell?.row === -1 && editingCell?.col === colIndex ? (
                    <Input
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                      onBlur={finishCellEdit}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') finishCellEdit()
                        if (e.key === 'Escape') setEditingCell(null)
                      }}
                      autoFocus
                      size="sm"
                      bg="midnight.800"
                      color={getColumnColor(colIndex)}
                      border="2px solid"
                      borderColor="plum.500"
                    />
                  ) : (
                    header || `Column ${colIndex + 1}`
                  )}
                  <div
                    onMouseDown={(e) => handleMouseDownResize(colIndex, e)}
                    style={{
                      position: 'absolute',
                      right: 0,
                      top: 0,
                      bottom: 0,
                      width: '4px',
                      cursor: 'col-resize',
                      backgroundColor: 'transparent',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#4E2A84'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent'
                    }}
                  />
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tableData.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                style={{
                  backgroundColor: rowIndex % 2 === 0 ? '#1B102A' : '#1F1233',
                  ...(rowHeights[rowIndex] ? { height: `${rowHeights[rowIndex]}px` } : {}),
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#2A1940'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = rowIndex % 2 === 0 ? '#1B102A' : '#1F1233'
                }}
              >
                <td
                  style={{
                    position: 'sticky',
                    left: 0,
                    backgroundColor: '#1B102A',
                    zIndex: 1,
                    width: `${rowIndexWidth}px`,
                    minWidth: `${rowIndexWidth}px`,
                    maxWidth: `${rowIndexWidth}px`,
                    borderRight: '1px solid #4E2A84',
                    borderBottom: '1px solid #4E2A84',
                    padding: '8px',
                    textAlign: 'center',
                    fontSize: '12px',
                    color: '#8B7AA8',
                    ...(rowHeights[rowIndex] ? { height: `${rowHeights[rowIndex]}px` } : {}),
                  }}
                >
                  {rowIndex + 1}
                  <div
                    onMouseDown={(e) => handleMouseDownResizeRow(rowIndex, e)}
                    style={{
                      position: 'absolute',
                      left: 0,
                      right: 0,
                      bottom: 0,
                      height: '4px',
                      cursor: 'row-resize',
                      backgroundColor: 'transparent',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#4E2A84'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent'
                    }}
                  />
                </td>
                {headers.map((_, colIndex) => {
                  const cellValue = row[colIndex] || ''
                  return (
                    <td
                      key={colIndex}
                      onClick={() => startCellEdit(rowIndex, colIndex)}
                      style={{
                        position: 'relative',
                        width: `${columnWidths[colIndex] || DEFAULT_COL_WIDTH}px`,
                        minWidth: `${columnWidths[colIndex] || DEFAULT_COL_WIDTH}px`,
                        maxWidth: `${columnWidths[colIndex] || DEFAULT_COL_WIDTH}px`,
                        borderRight: '1px solid #4E2A84',
                        borderBottom: '1px solid #4E2A84',
                        padding: '8px 12px',
                        fontSize: '14px',
                        color: getColumnColor(colIndex),
                        cursor: 'pointer',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        ...(rowHeights[rowIndex] ? { height: `${rowHeights[rowIndex]}px`, overflow: 'hidden' } : {}),
                      }}
                    >
                      {editingCell?.row === rowIndex && editingCell?.col === colIndex ? (
                        <Input
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          onBlur={finishCellEdit}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') finishCellEdit()
                            if (e.key === 'Escape') setEditingCell(null)
                          }}
                          autoFocus
                          size="sm"
                          bg="midnight.800"
                          color={getColumnColor(colIndex)}
                          border="2px solid"
                          borderColor="plum.500"
                        />
                      ) : (
                        cellValue
                      )}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </Box>
      )}
    </VStack>
  )
}
