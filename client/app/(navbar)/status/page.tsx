"use client";
import { useState, useEffect } from 'react';
import styles from '../style.module.css';
import fetchGarbageState from '@/app/helper';
import gPng from "@/public/graph.png";
import aPng from "@/public/amount.png";


export default function Status() {
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function fetchStatus() {
    try {
      const data = await fetchGarbageState();
      console.log(data.status); 
      setStatus(data.status);
      setError(null); // Clear any previous errors
    } catch (err) {
      console.error('Error fetching status:', err);
      setError('Failed to fetch status. Please try again later.');
    }
  }

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(() => {
      fetchStatus();
    }, 15000); // 15000 milliseconds = 15 seconds

    return () => clearInterval(interval); // Cleanup interval on component unmount
  }, []);

  return (
    <div className={styles.bg}>
      <div className={styles.container}>
        <div className={styles.videoPlaceholder}>
          <iframe 
            style={{
              background: '#E0D4CD',
              border: 'none',
              borderRadius: '2px',
              boxShadow: '0 2px 10px 0 rgba(70, 76, 79, .2)'
            }} 
            width="540" 
            height="480" 
            src={gPng.src}>
          </iframe>
        </div>

        <div className={styles.scrollableSection}>
          <div className={styles.topHalf}>
            <h2 className={styles.scrollableContainer}>
              Bin Status: {status !== null ? status : 'Waiting for data...'}
            </h2>
          </div>
          <div className={styles.bottomHalf}>
            <iframe
              style={{
                background: '#E0D4CD',
                border: 'none',
                borderRadius: '2px',
                boxShadow: '0 2px 10px 0 rgba(70, 76, 79, .2)'
              }}
              width="460"
              height="250"
              src={aPng.src}>
            </iframe>
          </div> 
        </div>
      </div>
    </div>
  );
}