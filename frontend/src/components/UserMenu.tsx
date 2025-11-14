import {
  Box,
  Button,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  Avatar,
  HStack,
  Text,
  VStack,
  useToast,
  Icon,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
} from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import { FiUser, FiSettings, FiLogOut, FiLogIn } from 'react-icons/fi'
import { FaGoogle, FaGithub } from 'react-icons/fa'
import axios from '../lib/axios'
import config from '../config'

interface User {
  id: string
  email: string
  display_name?: string
  avatar_url?: string
  provider: string
}

export default function UserMenu() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [isGuest, setIsGuest] = useState(false)
  const { isOpen, onOpen, onClose } = useDisclosure()
  const toast = useToast()

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    const token = localStorage.getItem('auth_token')
    const guestMode = localStorage.getItem('guest_mode')

    if (guestMode === 'true') {
      setIsGuest(true)
      setLoading(false)
      return
    }

    if (token) {
      try {
        const response = await axios.get(`${config.apiBaseUrl}/v1/auth/me`)
        setUser(response.data)
      } catch (error) {
        console.error('Failed to fetch user info:', error)
        localStorage.removeItem('auth_token')
        localStorage.removeItem('refresh_token')
      }
    }
    
    setLoading(false)
  }

  const handleLogin = (provider: 'google' | 'github') => {
    const apiUrl = import.meta.env.VITE_API_BASE_URL || window.location.origin + '/api'
    window.location.href = `${apiUrl}/v1/auth/login/${provider}`
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('guest_mode')
    setUser(null)
    setIsGuest(false)
    window.location.reload()
  }

  const openAccountSettings = () => {
    onOpen()
  }

  if (loading) {
    return null
  }

  // Show login button for non-authenticated users
  if (!user && !isGuest) {
    return (
      <>
        <Button
          leftIcon={<Icon as={FiLogIn} />}
          onClick={onOpen}
          size="sm"
          variant="outline"
          colorScheme="blue"
          _hover={{ bg: 'blue.500', color: 'white' }}
        >
          Log In
        </Button>

        <Modal isOpen={isOpen} onClose={onClose} isCentered>
          <ModalOverlay backdropFilter="blur(4px)" />
          <ModalContent bg="midnight.800" borderColor="midnight.700" borderWidth={1}>
            <ModalHeader color="gray.100">Log in to Gunpowder Splash</ModalHeader>
            <ModalCloseButton color="gray.400" />
            <ModalBody pb={6}>
              <VStack spacing={3}>
                <Button
                  leftIcon={<Icon as={FaGoogle} />}
                  onClick={() => handleLogin('google')}
                  width="100%"
                  colorScheme="red"
                  variant="solid"
                >
                  Continue with Google
                </Button>
                <Button
                  leftIcon={<Icon as={FaGithub} />}
                  onClick={() => handleLogin('github')}
                  width="100%"
                  colorScheme="gray"
                  variant="solid"
                >
                  Continue with GitHub
                </Button>
              </VStack>
            </ModalBody>
          </ModalContent>
        </Modal>
      </>
    )
  }

  // Show guest user indicator
  if (isGuest) {
    return (
      <Menu>
        <MenuButton>
          <HStack spacing={2} cursor="pointer" _hover={{ opacity: 0.8 }}>
            <Avatar size="sm" name="Guest" bg="gray.600" />
            <Text fontSize="sm" color="gray.300" display={{ base: 'none', md: 'block' }}>
              Guest
            </Text>
          </HStack>
        </MenuButton>
        <MenuList bg="midnight.800" borderColor="midnight.700">
          <MenuItem
            icon={<Icon as={FiLogIn} />}
            onClick={onOpen}
            bg="midnight.800"
            _hover={{ bg: 'midnight.700' }}
            color="gray.200"
          >
            Log in to save work
          </MenuItem>
          <MenuDivider />
          <MenuItem
            icon={<Icon as={FiLogOut} />}
            onClick={handleLogout}
            bg="midnight.800"
            _hover={{ bg: 'midnight.700' }}
            color="gray.200"
          >
            Exit Guest Mode
          </MenuItem>
        </MenuList>
        
        <Modal isOpen={isOpen} onClose={onClose} isCentered>
          <ModalOverlay backdropFilter="blur(4px)" />
          <ModalContent bg="midnight.800" borderColor="midnight.700" borderWidth={1}>
            <ModalHeader color="gray.100">Log in to save your work</ModalHeader>
            <ModalCloseButton color="gray.400" />
            <ModalBody pb={6}>
              <VStack spacing={3}>
                <Button
                  leftIcon={<Icon as={FaGoogle} />}
                  onClick={() => handleLogin('google')}
                  width="100%"
                  colorScheme="red"
                  variant="solid"
                >
                  Continue with Google
                </Button>
                <Button
                  leftIcon={<Icon as={FaGithub} />}
                  onClick={() => handleLogin('github')}
                  width="100%"
                  colorScheme="gray"
                  variant="solid"
                >
                  Continue with GitHub
                </Button>
              </VStack>
            </ModalBody>
          </ModalContent>
        </Modal>
      </Menu>
    )
  }

  // Show user profile menu for authenticated users
  return (
    <>
      <Menu>
        <MenuButton>
          <HStack spacing={2} cursor="pointer" _hover={{ opacity: 0.8 }}>
            <Avatar
              size="sm"
              name={user?.display_name || user?.email}
              src={user?.avatar_url}
            />
            <Text fontSize="sm" color="gray.300" display={{ base: 'none', md: 'block' }}>
              {user?.display_name || user?.email?.split('@')[0]}
            </Text>
          </HStack>
        </MenuButton>
        <MenuList bg="midnight.800" borderColor="midnight.700">
          <Box px={4} py={3}>
            <VStack align="start" spacing={1}>
              <Text fontSize="sm" fontWeight="bold" color="gray.100">
                {user?.display_name}
              </Text>
              <Text fontSize="xs" color="gray.400">
                {user?.email}
              </Text>
              <Text fontSize="xs" color="gray.500">
                via {user?.provider}
              </Text>
            </VStack>
          </Box>
          <MenuDivider />
          <MenuItem
            icon={<Icon as={FiUser} />}
            onClick={openAccountSettings}
            bg="midnight.800"
            _hover={{ bg: 'midnight.700' }}
            color="gray.200"
          >
            Profile
          </MenuItem>
          <MenuItem
            icon={<Icon as={FiSettings} />}
            onClick={openAccountSettings}
            bg="midnight.800"
            _hover={{ bg: 'midnight.700' }}
            color="gray.200"
          >
            Account Settings
          </MenuItem>
          <MenuDivider />
          <MenuItem
            icon={<Icon as={FiLogOut} />}
            onClick={handleLogout}
            bg="midnight.800"
            _hover={{ bg: 'midnight.700' }}
            color="red.300"
          >
            Log Out
          </MenuItem>
        </MenuList>
      </Menu>

      {/* Account Settings Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay backdropFilter="blur(4px)" />
        <ModalContent bg="midnight.800" borderColor="midnight.700" borderWidth={1}>
          <ModalHeader color="gray.100">Account Settings</ModalHeader>
          <ModalCloseButton color="gray.400" />
          <ModalBody pb={6}>
            <VStack spacing={4} align="stretch">
              <Box>
                <Text fontSize="sm" fontWeight="bold" color="gray.300" mb={2}>
                  Profile
                </Text>
                <HStack spacing={4}>
                  <Avatar
                    size="lg"
                    name={user?.display_name || user?.email}
                    src={user?.avatar_url}
                  />
                  <VStack align="start" spacing={1}>
                    <Text color="gray.100">{user?.display_name}</Text>
                    <Text fontSize="sm" color="gray.400">
                      {user?.email}
                    </Text>
                    <Text fontSize="xs" color="gray.500">
                      Authenticated via {user?.provider}
                    </Text>
                  </VStack>
                </HStack>
              </Box>

              <MenuDivider />

              <Box>
                <Text fontSize="sm" fontWeight="bold" color="gray.300" mb={2}>
                  Account Information
                </Text>
                <VStack align="stretch" spacing={2}>
                  <HStack justify="space-between">
                    <Text fontSize="sm" color="gray.400">
                      User ID
                    </Text>
                    <Text fontSize="sm" color="gray.300" fontFamily="mono">
                      {user?.id.slice(0, 8)}...
                    </Text>
                  </HStack>
                  <HStack justify="space-between">
                    <Text fontSize="sm" color="gray.400">
                      Provider
                    </Text>
                    <Text fontSize="sm" color="gray.300">
                      {user?.provider}
                    </Text>
                  </HStack>
                </VStack>
              </Box>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  )
}

