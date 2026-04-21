import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

const dataFilePath = path.join(process.cwd(), 'data', 'clients.json');

// Ensure the data directory and file exist
async function initDataFile() {
  const dataDir = path.join(process.cwd(), 'data');
  try {
    await fs.mkdir(dataDir, { recursive: true });
    try {
      await fs.access(dataFilePath);
    } catch {
      await fs.writeFile(dataFilePath, JSON.stringify([]));
    }
  } catch (error) {
    console.error('Error initializing data file:', error);
  }
}

export async function POST(request) {
  try {
    await initDataFile();
    const data = await request.json();
    
    // Read existing data
    const fileContent = await fs.readFile(dataFilePath, 'utf-8');
    const clients = JSON.parse(fileContent);
    
    // Add new client
    const newClient = {
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
      ...data,
    };
    
    clients.push(newClient);
    
    // Save to file
    await fs.writeFile(dataFilePath, JSON.stringify(clients, null, 2));
    
    return NextResponse.json({ success: true, client: newClient });
  } catch (error) {
    console.error('Error processing onboarding submission:', error);
    return NextResponse.json({ error: 'Failed to process submission' }, { status: 500 });
  }
}

export async function GET() {
  try {
    await initDataFile();
    const fileContent = await fs.readFile(dataFilePath, 'utf-8');
    const clients = JSON.parse(fileContent);
    
    // Sort by newest first
    clients.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    
    return NextResponse.json(clients);
  } catch (error) {
    return NextResponse.json({ error: 'Failed to retrieve clients' }, { status: 500 });
  }
}
