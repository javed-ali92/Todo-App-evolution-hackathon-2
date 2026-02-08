// Authentication utilities for the Todo App frontend

/**
 * Checks if the user is authenticated by verifying the existence and validity of the JWT token
 * @returns {boolean} True if the user is authenticated, false otherwise
 */
export const isAuthenticated = (): boolean => {
  const storedSession = localStorage.getItem('userSession');

  if (!storedSession) {
    return false;
  }

  try {
    const session = JSON.parse(storedSession);

    // Check if the token exists and hasn't expired
    if (session.accessToken && session.expiryTime) {
      const expiryTime = new Date(session.expiryTime);
      const currentTime = new Date();

      return currentTime < expiryTime;
    }

    return false;
  } catch (error) {
    console.error('Error parsing user session:', error);
    return false;
  }
};

/**
 * Gets the current user's session data
 * @returns {Object|null} The user session object or null if not authenticated
 */
export const getCurrentUserSession = () => {
  if (!isAuthenticated()) {
    return null;
  }

  try {
    const storedSession = localStorage.getItem('userSession');
    return storedSession ? JSON.parse(storedSession) : null;
  } catch (error) {
    console.error('Error getting current user session:', error);
    return null;
  }
};

/**
 * Stores the user session in local storage
 * @param {Object} session - The session object to store
 */
export const storeUserSession = (session: any): void => {
  try {
    // Calculate expiry time (1 hour from now)
    const expiryTime = new Date();
    expiryTime.setHours(expiryTime.getHours() + 1);

    const sessionWithExpiry = {
      ...session,
      expiryTime: expiryTime.toISOString(),
    };

    localStorage.setItem('userSession', JSON.stringify(sessionWithExpiry));
  } catch (error) {
    console.error('Error storing user session:', error);
  }
};

/**
 * Clears the user session from local storage
 */
export const clearUserSession = (): void => {
  try {
    localStorage.removeItem('userSession');
  } catch (error) {
    console.error('Error clearing user session:', error);
  }
};

/**
 * Attaches the JWT token to the request headers
 * @param {Object} headers - The existing headers object
 * @returns {Object} The headers object with the Authorization header added
 */
export const attachAuthToken = (headers: Record<string, string>): Record<string, string> => {
  const session = getCurrentUserSession();

  if (session && session.accessToken) {
    return {
      ...headers,
      'Authorization': `Bearer ${session.accessToken}`,
    };
  }

  return headers;
};

/**
 * Refreshes the user's authentication token
 * @returns {Promise<boolean>} True if the token was refreshed successfully, false otherwise
 */
export const refreshAuthToken = async (): Promise<boolean> => {
  // In a real implementation, this would call an API endpoint to refresh the token
  // For now, we'll just return true to indicate success
  try {
    const session = getCurrentUserSession();

    if (!session) {
      return false;
    }

    // Calculate new expiry time (1 hour from now)
    const newExpiryTime = new Date();
    newExpiryTime.setHours(newExpiryTime.getHours() + 1);

    const updatedSession = {
      ...session,
      expiryTime: newExpiryTime.toISOString(),
    };

    storeUserSession(updatedSession);
    return true;
  } catch (error) {
    console.error('Error refreshing auth token:', error);
    return false;
  }
};