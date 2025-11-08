import { useState } from 'react'
import { Box, Button, Text, VStack, HStack } from '@chakra-ui/react'
import axios from 'axios'

interface DataInfo {
  rows: number
  columns: number
  columnNames: string[]
  data: any[]
}

function DataExplorer() {
  const [dataInfo, setDataInfo] = useState<DataInfo | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsLoading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post('/api/data/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      const result = response.data
      
      if (result.success) {
        // Now fetch the preview
        const previewResponse = await axios.get(`/api/data/preview/${result.dataset_name}`)
        const previewData = previewResponse.data
        
        setDataInfo({
          rows: previewData.total_rows,
          columns: previewData.columns.length,
          columnNames: previewData.columns,
          data: previewData.data
        })
        
        alert(`Dataset "${result.dataset_name}" uploaded successfully!`)
      }
    } catch (error: any) {
      console.error('Error uploading file:', error)
      alert(error.response?.data?.detail || 'Error uploading file')
    } finally {
      setIsLoading(false)
    }
  }

  const exportAsCSV = () => {
    if (!dataInfo) return

    const csv = [
      dataInfo.columnNames.join(','),
      ...dataInfo.data.map(row => 
        dataInfo.columnNames.map(col => row[col] || '').join(',')
      )
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'export.csv'
    a.click()
  }

  const exportAsJSON = () => {
    if (!dataInfo) return

    const json = JSON.stringify(dataInfo.data, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'export.json'
    a.click()
  }

  return (
    <Box h="100%">
      <VStack align="stretch" gap={4} h="100%">
        <HStack justify="space-between">
          <Text fontSize="lg" color="midnight.400" fontWeight="bold">
            Data Explorer
          </Text>
          <HStack gap={2}>
            <label htmlFor="file-upload">
              <Button
                size="sm"
                as="span"
                cursor="pointer"
                loading={isLoading}
              >
                📁 Upload Data
              </Button>
            </label>
            <input
              id="file-upload"
              type="file"
              accept=".json,.csv"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
            {dataInfo && (
              <>
                <Button size="sm" onClick={exportAsCSV}>
                  ⬇ CSV
                </Button>
                <Button size="sm" onClick={exportAsJSON}>
                  ⬇ JSON
                </Button>
              </>
            )}
          </HStack>
        </HStack>

        {!dataInfo ? (
          <VStack h="100%" justify="center" gap={4}>
            <Text fontSize="lg" color="midnight.400">
              Upload a JSON or CSV file to explore
            </Text>
            <label htmlFor="file-upload">
              <Button
                as="span"
                cursor="pointer"
                colorScheme="purple"
                size="lg"
              >
                📁 Choose File
              </Button>
            </label>
          </VStack>
        ) : (
          <>
            <HStack gap={6} p={4} bg="rgba(27, 16, 42, 0.5)" borderRadius="md">
              <Box>
                <Text fontSize="sm" color="midnight.500">Rows</Text>
                <Text fontSize="xl" color="midnight.400" fontWeight="bold">
                  {dataInfo.rows.toLocaleString()}
                </Text>
              </Box>
              <Box>
                <Text fontSize="sm" color="midnight.500">Columns</Text>
                <Text fontSize="xl" color="midnight.400" fontWeight="bold">
                  {dataInfo.columns}
                </Text>
              </Box>
            </HStack>

            <Box 
              flex="1" 
              overflowY="auto" 
              border="1px solid" 
              borderColor="midnight.700" 
              borderRadius="md"
            >
              <Box as="table" w="100%" fontSize="sm">
                <Box as="thead" bg="midnight.800" position="sticky" top={0}>
                  <Box as="tr">
                    {dataInfo.columnNames.map((col) => (
                      <Box
                        as="th"
                        key={col}
                        color="midnight.400"
                        p={2}
                        textAlign="left"
                        borderBottom="1px solid"
                        borderColor="midnight.700"
                      >
                        {col}
                      </Box>
                    ))}
                  </Box>
                </Box>
                <Box as="tbody">
                  {dataInfo.data.map((row, idx) => (
                    <Box
                      as="tr"
                      key={idx}
                      _hover={{ bg: 'rgba(128, 90, 213, 0.1)' }}
                    >
                      {dataInfo.columnNames.map((col) => (
                        <Box
                          as="td"
                          key={col}
                          color="midnight.400"
                          p={2}
                          borderBottom="1px solid"
                          borderColor="midnight.700"
                        >
                          {String(row[col] || '')}
                        </Box>
                      ))}
                    </Box>
                  ))}
                </Box>
              </Box>
            </Box>

            {dataInfo.rows > 100 && (
              <Text fontSize="sm" color="midnight.500" textAlign="center">
                Showing first 100 of {dataInfo.rows.toLocaleString()} rows
              </Text>
            )}
          </>
        )}
      </VStack>
    </Box>
  )
}

export default DataExplorer
