import { Box } from '@chakra-ui/react'
import { useState } from 'react'
import CodeEditor from './tabs/CodeEditor'
import WebEdit from './tabs/WebEdit'
import Templates from './tabs/Templates'
import DataExplorer from './tabs/DataExplorer'
import System from './tabs/System'
import History from './tabs/History'
import QueryFilter from './tabs/QueryFilter'

function MainContent() {
  const [activeTab, setActiveTab] = useState(0)

  const tabs = [
    'Code Editor',
    'Web-Edit',
    'Data Explorer',
    'Query & Filter',
    'Templates',
    'History',
    'System'
  ]

  return (
    <Box h="100%" p={6}>
      <Box h="100%">
        <Box borderColor="midnight.700" bg="rgba(78, 42, 132, 0.2)" p={2} borderRadius="8px 8px 0 0" display="flex" gap={2}>
          {tabs.map((tab, index) => (
            <Box
              key={tab}
              as="button"
              px={4}
              py={2}
              borderRadius="6px 6px 0 0"
              bg={activeTab === index ? 'midnight.700' : 'transparent'}
              color={activeTab === index ? 'white' : 'midnight.500'}
              border="1px solid"
              borderColor="midnight.700"
              onClick={() => setActiveTab(index)}
              cursor="pointer"
              fontWeight="600"
              _hover={{
                bg: activeTab === index ? 'midnight.700' : 'rgba(78, 42, 132, 0.3)',
                color: 'white'
              }}
            >
              {tab}
            </Box>
          ))}
        </Box>

        <Box bg="rgba(45, 27, 71, 0.4)" borderRadius="0 0 12px 12px" p={6} h="calc(100% - 50px)" overflow="auto">
          {activeTab === 0 && <CodeEditor />}
          {activeTab === 1 && <WebEdit />}
          {activeTab === 2 && <DataExplorer />}
          {activeTab === 3 && <QueryFilter />}
          {activeTab === 4 && <Templates />}
          {activeTab === 5 && <History />}
          {activeTab === 6 && <System />}
        </Box>
      </Box>
    </Box>
  )
}

export default MainContent
