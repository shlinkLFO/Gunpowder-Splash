import { useState } from 'react'
import { Box, Button, Text, VStack, HStack, Input } from '@chakra-ui/react'
import Editor from '@monaco-editor/react'
import axios from 'axios'

interface QueryResult {
  columns: string[]
  data: any[]
  rowCount: number
}

function QueryFilter() {
  const [sqlQuery, setSqlQuery] = useState(`-- Write SQL queries to filter and analyze data
-- Example: SELECT * FROM df WHERE column_name = 'value'

SELECT * FROM df LIMIT 10;`)

  const [results, setResults] = useState<QueryResult | null>(null)
  const [isExecuting, setIsExecuting] = useState(false)
  const [error, setError] = useState('')
  
  const [filterColumn, setFilterColumn] = useState('')
  const [filterValue, setFilterValue] = useState('')
  const [searchText, setSearchText] = useState('')

  const executeQuery = async () => {
    setIsExecuting(true)
    setError('')
    
    try {
      const response = await axios.post('/api/data/query', { query: sqlQuery })
      
      if (response.data.success) {
        setResults({
          columns: response.data.columns,
          data: response.data.data,
          rowCount: response.data.row_count
        })
      } else {
        setError(response.data.error || 'Query failed')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Query execution failed')
    } finally {
      setIsExecuting(false)
    }
  }

  const applyFilter = () => {
    if (!filterColumn || !filterValue) {
      alert('Please enter both column and value')
      return
    }
    
    const filterQuery = `SELECT * FROM df WHERE ${filterColumn} = '${filterValue}' LIMIT 100;`
    setSqlQuery(filterQuery)
  }

  const applySearch = async () => {
    if (!searchText) {
      alert('Please enter search text')
      return
    }
    
    setIsExecuting(true)
    setError('')
    
    try {
      const response = await axios.post('/api/data/search', {
        dataset_name: 'df',
        search_text: searchText
      })
      
      if (response.data.success) {
        setResults({
          columns: response.data.columns,
          data: response.data.data,
          rowCount: response.data.row_count
        })
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed')
    } finally {
      setIsExecuting(false)
    }
  }

  return (
    <Box h="100%">
      <VStack align="stretch" gap={4} h="100%">
        <Text fontSize="lg" color="midnight.400" fontWeight="bold">
          Query & Filter
        </Text>

        <HStack gap={4}>
          <Box
            flex="1"
            p={4}
            bg="rgba(27, 16, 42, 0.5)"
            border="1px solid"
            borderColor="midnight.700"
            borderRadius="md"
          >
            <Text fontSize="sm" color="midnight.400" fontWeight="bold" mb={2}>
              Quick Filter
            </Text>
            <VStack align="stretch" gap={2}>
              <Input
                size="sm"
                placeholder="Column name"
                value={filterColumn}
                onChange={(e) => setFilterColumn(e.target.value)}
              />
              <Input
                size="sm"
                placeholder="Filter value"
                value={filterValue}
                onChange={(e) => setFilterValue(e.target.value)}
              />
              <Button size="sm" onClick={applyFilter}>
                Apply Filter
              </Button>
            </VStack>
          </Box>

          <Box
            flex="1"
            p={4}
            bg="rgba(27, 16, 42, 0.5)"
            border="1px solid"
            borderColor="midnight.700"
            borderRadius="md"
          >
            <Text fontSize="sm" color="midnight.400" fontWeight="bold" mb={2}>
              Text Search
            </Text>
            <VStack align="stretch" gap={2}>
              <Input
                size="sm"
                placeholder="Search text"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
              />
              <Button size="sm" onClick={applySearch}>
                Search
              </Button>
            </VStack>
          </Box>
        </HStack>

        <Box
          flex="1"
          border="1px solid"
          borderColor="midnight.700"
          borderRadius="md"
          overflow="hidden"
        >
          <HStack bg="midnight.800" px={3} py={2} justify="space-between">
            <Text fontSize="sm" color="midnight.400" fontWeight="bold">
              SQL Query Editor
            </Text>
            <Button
              size="sm"
              onClick={executeQuery}
              isLoading={isExecuting}
              colorScheme="green"
            >
              ▶ Execute Query
            </Button>
          </HStack>
          <Box h="calc(100% - 50px)">
            <Editor
              height="100%"
              language="sql"
              value={sqlQuery}
              onChange={(value) => setSqlQuery(value || '')}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                automaticLayout: true,
              }}
            />
          </Box>
        </Box>

        {error && (
          <Box
            p={3}
            bg="rgba(220, 38, 38, 0.1)"
            border="1px solid"
            borderColor="red.500"
            borderRadius="md"
          >
            <Text fontSize="sm" color="red.400">
              {error}
            </Text>
          </Box>
        )}

        {results && (
          <Box
            p={4}
            bg="rgba(27, 16, 42, 0.5)"
            border="1px solid"
            borderColor="midnight.700"
            borderRadius="md"
            maxH="300px"
            overflowY="auto"
          >
            <HStack justify="space-between" mb={3}>
              <Text fontSize="sm" color="midnight.400" fontWeight="bold">
                Query Results
              </Text>
              <Text fontSize="sm" color="midnight.500">
                {results.rowCount} rows
              </Text>
            </HStack>

            <Box as="table" w="100%" fontSize="sm">
              <Box as="thead" bg="midnight.800">
                <Box as="tr">
                  {results.columns.map((col) => (
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
                {results.data.map((row, idx) => (
                  <Box as="tr" key={idx} _hover={{ bg: 'rgba(128, 90, 213, 0.1)' }}>
                    {results.columns.map((col) => (
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
        )}

        <Box
          p={3}
          bg="rgba(27, 16, 42, 0.5)"
          border="1px solid"
          borderColor="midnight.700"
          borderRadius="md"
        >
          <Text fontSize="xs" color="midnight.500">
            💡 Tip: Load data using the Data Explorer tab or execute Python code to create DataFrames.
            Then query them using SQL syntax (e.g., SELECT * FROM df WHERE column = 'value').
          </Text>
        </Box>
      </VStack>
    </Box>
  )
}

export default QueryFilter
