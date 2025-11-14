import { Box, Button, Stack, Text } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import { FiLogIn } from 'react-icons/fi'
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
  const [showLogin, setShowLogin] = useState(false)
  const [showMenu, setShowMenu] = useState(false)

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
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
          // Don't remove token on error, just continue
        }
      }
    } catch (error) {
      console.error('Error in checkAuthStatus:', error)
    } finally {
      setLoading(false)
    }
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

  if (loading) {
    return null
  }

  // Show login button for non-authenticated users
  if (!user && !isGuest) {
    return (
      <Box position="relative">
        <Button
          onClick={() => setShowLogin(!showLogin)}
          size="sm"
          variant="outline"
          colorScheme="blue"
        >
          <FiLogIn style={{ marginRight: '8px' }} />
          Log In
        </Button>

        {showLogin && (
          <Box
            position="absolute"
            right={0}
            top="calc(100% + 8px)"
            bg="midnight.800"
            borderRadius="md"
            borderWidth="1px"
            borderColor="midnight.700"
            p={4}
            minW="280px"
            boxShadow="lg"
            zIndex={1000}
          >
            <Text color="gray.100" mb={3} fontWeight="medium">
              Log in to Gunpowder Splash
            </Text>
            <Stack gap={2}>
              <Button
                onClick={() => handleLogin('google')}
                width="100%"
                colorScheme="red"
                size="sm"
              >
                <FaGoogle style={{ marginRight: '8px' }} />
                Continue with Google
              </Button>
              <Button
                onClick={() => handleLogin('github')}
                width="100%"
                colorScheme="gray"
                size="sm"
              >
                <FaGithub style={{ marginRight: '8px' }} />
                Continue with GitHub
              </Button>
            </Stack>
          </Box>
        )}
      </Box>
    )
  }

  // Show guest or user menu
  const displayName = user?.display_name || (isGuest ? 'Guest' : user?.email?.split('@')[0])
  const avatarUrl = user?.avatar_url

  return (
    <Box position="relative">
      <Stack
        direction="row"
        align="center"
        gap={2}
        cursor="pointer"
        onClick={() => setShowMenu(!showMenu)}
        _hover={{ opacity: 0.8 }}
      >
        {avatarUrl ? (
          <Box
            w="32px"
            h="32px"
            borderRadius="full"
            overflow="hidden"
            bg="gray.600"
          >
            <img
              src={avatarUrl}
              alt={displayName}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          </Box>
        ) : (
          <Box
            w="32px"
            h="32px"
            borderRadius="full"
            bg="gray.600"
            display="flex"
            alignItems="center"
            justifyContent="center"
            color="white"
            fontSize="sm"
            fontWeight="bold"
          >
            {displayName?.charAt(0).toUpperCase()}
          </Box>
        )}
        <Text fontSize="sm" color="gray.300" display={{ base: 'none', md: 'block' }}>
          {displayName}
        </Text>
      </Stack>

      {showMenu && (
        <Box
          position="absolute"
          right={0}
          top="calc(100% + 8px)"
          bg="midnight.800"
          borderRadius="md"
          borderWidth="1px"
          borderColor="midnight.700"
          minW="240px"
          boxShadow="lg"
          zIndex={1000}
        >
          {user && (
            <>
              <Box p={4} borderBottomWidth="1px" borderColor="midnight.700">
                <Text fontSize="sm" fontWeight="bold" color="gray.100">
                  {user.display_name}
                </Text>
                <Text fontSize="xs" color="gray.400">
                  {user.email}
                </Text>
                <Text fontSize="xs" color="gray.500" mt={1}>
                  via {user.provider}
                </Text>
              </Box>
            </>
          )}

          {isGuest && (
            <Box
              p={3}
              cursor="pointer"
              _hover={{ bg: 'midnight.700' }}
              color="gray.200"
              onClick={() => setShowLogin(true)}
            >
              <Text fontSize="sm">Log in to save work</Text>
            </Box>
          )}

          <Box
            p={3}
            cursor="pointer"
            _hover={{ bg: 'midnight.700' }}
            color="red.300"
            onClick={handleLogout}
            borderTopWidth={user ? "1px" : undefined}
            borderColor="midnight.700"
          >
            <Text fontSize="sm">
              {isGuest ? 'Exit Guest Mode' : 'Log Out'}
            </Text>
          </Box>
        </Box>
      )}
    </Box>
  )
}
