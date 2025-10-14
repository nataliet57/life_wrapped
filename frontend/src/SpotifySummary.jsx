import React from 'react';

export default function SpotifySummary({ tracks }) {
  if (!tracks?.length) {
    return null;
  }

  return (
    <div
      className="spotify-summary-row"
      style={{
        display: 'flex',
        gap: '24px',
        overflowX: 'auto',
        padding: '12px 0',
        fontFamily: 'Helvetica, Arial, sans-serif',
      }}
    >
      {tracks.map((track) => {
        const {
          rank,
          track: name,
          artist,
          album,
          spotify_url: spotifyUrl,
          cover_art: coverArt,
        } = track;
        const key =
          rank ?? spotifyUrl ?? `${name ?? 'unknown'}-${artist ?? 'artist'}`;

        const imageElement = coverArt ? (
          <img
            src={coverArt}
            alt={name ? `${name} cover art` : 'Spotify track cover art'}
            style={{
              width: '360px',
              height: '360px',
              objectFit: 'cover',
              borderRadius: '8px',
            }}
          />
        ) : (
          <div
            style={{
              width: '360px',
              height: '360px',
              backgroundColor: '#e5e7eb',
              borderRadius: '8px',
            }}
            aria-hidden="true"
          />
        );

        return (
          <div
            key={key}
            className="spotify-summary-card"
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              minWidth: '360px',
            }}
          >
            {spotifyUrl ? (
              <a
                href={spotifyUrl}
                target="_blank"
                rel="noopener noreferrer"
                style={{ display: 'block' }}
              >
                {imageElement}
              </a>
            ) : (
              imageElement
            )}
            <div style={{ marginTop: '12px' }}>
              <p style={{ margin: '0 0 4px', fontWeight: 600 }}>
                {rank != null ? `#${rank} ` : ''}
                {name ?? 'Unknown track'}
              </p>
              <p style={{ margin: '0 0 4px', color: '#4b5563' }}>
                {artist ?? 'Unknown artist'}
              </p>
              <p style={{ margin: 0, color: '#6b7280' }}>
                {album ?? 'Unknown album'}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
