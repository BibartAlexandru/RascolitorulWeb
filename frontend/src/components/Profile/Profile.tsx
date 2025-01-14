import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Profile.css';

interface SearchHistory {
  search_text: string;
  timestamp: string;
}

interface BlockedSite {
  site_url: string;
}

const Profile: React.FC = () => {
  const [userName, setUserName] = useState<string>('');
  const [searchHistory, setSearchHistory] = useState<SearchHistory[]>([]);
  const [blockedSites, setBlockedSites] = useState<BlockedSite[]>([]);
  const [newBlockedSite, setNewBlockedSite] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true); // Loading state

  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        const [userResponse, historyResponse, blockedSitesResponse] = await Promise.all([
          axios.get('/prajitura/profile'),
          axios.get('/prajitura/profile/search-history'),
          axios.get('/prajitura/profile/blocked-sites') // Request blocked sites data
        ]);

        setUserName(userResponse.data.username);
        setSearchHistory(historyResponse.data);
        setBlockedSites(blockedSitesResponse.data);
      } catch (err) {
        setError('Failed to fetch profile data');
        console.error(err);
      } finally {
        setLoading(false); // Stop loading once data is fetched
      }
    };

    fetchProfileData();
  }, []);

  const handleBlockSite = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

      await axios.post('/prajitura/profile/block-site', { site_url: newBlockedSite });
      setBlockedSites((prev) => [...prev, { site_url: newBlockedSite }]);
      setNewBlockedSite('');


  };

  if (loading) {
    return <div>Loading profile...</div>; // Loading state feedback
  }

  return (
    <div className="profile-page">
      <h2>User Profile</h2>
      {error && <p className="error">{error}</p>}

      <div className="user-info">
        <h3>Welcome, {userName}!</h3>
      </div>

      <div className="search-history">
        <h4>Search History:</h4>
        {searchHistory.length === 0 ? (
          <p>No search history found.</p>
        ) : (
          <ul>
            {searchHistory.map((search, index) => (
              <li key={index}>
                <strong>{search.search_text}</strong> (searched on{' '}
                {new Date(search.timestamp).toLocaleString()})
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="blocked-sites">
        <h4>Blocked Sites:</h4>
        <form onSubmit={handleBlockSite}>
          <label>Block a site:</label>
          <input
            type="text"
            value={newBlockedSite}
            onChange={(e) => setNewBlockedSite(e.target.value)}
            placeholder="Enter site URL"
            required
          />
          <button type="submit">Block</button>
        </form>

        <ul>
          {blockedSites.length === 0 ? (
            <p>No blocked sites.</p>
          ) : (
            blockedSites.map((blockedSite, index) => (
              <li key={index}>{blockedSite.site_url}</li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
};

export default Profile;
