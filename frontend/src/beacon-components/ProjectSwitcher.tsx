/**
 * Beacon Studio - Project Switcher Component
 * 
 * Global project switcher that appears in the upper-left corner
 * Allows users to switch between projects and create new ones
 */

import React, { useState, useEffect } from 'react';
import axios from '../lib/axios';

interface Project {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

interface Workspace {
  id: string;
  plan_name: string;
  my_role: string;
}

interface ProjectSwitcherProps {
  currentProjectId?: string;
  onProjectSwitch: (projectId: string) => void;
}

export const ProjectSwitcher: React.FC<ProjectSwitcherProps> = ({
  currentProjectId,
  onProjectSwitch
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState<string>('');
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDescription, setNewProjectDescription] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadWorkspaces();
  }, []);

  useEffect(() => {
    if (selectedWorkspaceId) {
      loadProjects(selectedWorkspaceId);
    }
  }, [selectedWorkspaceId]);

  useEffect(() => {
    if (currentProjectId && projects.length > 0) {
      const project = projects.find(p => p.id === currentProjectId);
      setCurrentProject(project || null);
    }
  }, [currentProjectId, projects]);

  const loadWorkspaces = async () => {
    try {
      const response = await axios.get('/api/v1/workspaces', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('auth_token')}`
        }
      });
      setWorkspaces(response.data);
      
      // Select first workspace by default
      if (response.data.length > 0 && !selectedWorkspaceId) {
        setSelectedWorkspaceId(response.data[0].id);
      }
    } catch (error) {
      console.error('Failed to load workspaces:', error);
    }
  };

  const loadProjects = async (workspaceId: string) => {
    try {
      const response = await axios.get(`/api/v1/projects?workspace_id=${workspaceId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('auth_token')}`
        }
      });
      setProjects(response.data);
    } catch (error) {
      console.error('Failed to load projects:', error);
    }
  };

  const handleCreateProject = async () => {
    if (!newProjectName.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post('/api/v1/projects', {
        workspace_id: selectedWorkspaceId,
        name: newProjectName,
        description: newProjectDescription
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('auth_token')}`
        }
      });

      // Add to projects list
      setProjects([...projects, response.data]);
      
      // Switch to new project
      onProjectSwitch(response.data.id);
      
      // Close modal
      setShowCreateModal(false);
      setNewProjectName('');
      setNewProjectDescription('');
      setIsOpen(false);
    } catch (error) {
      console.error('Failed to create project:', error);
      alert('Failed to create project. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleProjectSelect = (projectId: string) => {
    onProjectSwitch(projectId);
    setIsOpen(false);
  };

  return (
    <>
      {/* Project Button (Global, Upper-Left) */}
      <button
        className="beacon-project-button"
        onClick={() => setIsOpen(!isOpen)}
        title="Switch Project"
      >
        <span className="project-icon">📁</span>
        <span className="project-name">
          {currentProject?.name || 'Select Project'}
        </span>
        <span className="dropdown-arrow">▼</span>
      </button>

      {/* Project Switcher Dropdown */}
      {isOpen && (
        <div className="beacon-project-switcher-overlay" onClick={() => setIsOpen(false)}>
          <div className="beacon-project-switcher" onClick={(e) => e.stopPropagation()}>
            <div className="switcher-header">
              <h2>Switch Project</h2>
              <button className="close-btn" onClick={() => setIsOpen(false)}>×</button>
            </div>

            {/* Workspace Selector */}
            <div className="workspace-selector">
              <label>Workspace:</label>
              <select
                value={selectedWorkspaceId}
                onChange={(e) => setSelectedWorkspaceId(e.target.value)}
              >
                {workspaces.map((workspace) => (
                  <option key={workspace.id} value={workspace.id}>
                    {workspace.plan_name} ({workspace.my_role})
                  </option>
                ))}
              </select>
            </div>

            {/* Projects List */}
            <div className="projects-list">
              {projects.length === 0 ? (
                <div className="empty-state">
                  <p>No projects in this workspace</p>
                  <button onClick={() => setShowCreateModal(true)}>
                    Create Your First Project
                  </button>
                </div>
              ) : (
                <>
                  {projects.map((project) => (
                    <div
                      key={project.id}
                      className={`project-item ${project.id === currentProjectId ? 'active' : ''}`}
                      onClick={() => handleProjectSelect(project.id)}
                    >
                      <div className="project-icon">📁</div>
                      <div className="project-info">
                        <div className="project-name">{project.name}</div>
                        {project.description && (
                          <div className="project-description">{project.description}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </>
              )}
            </div>

            {/* Create New Project Button */}
            {projects.length > 0 && (
              <div className="switcher-footer">
                <button
                  className="create-project-btn"
                  onClick={() => setShowCreateModal(true)}
                >
                  + Create New Project
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="beacon-modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="beacon-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create New Project</h2>
              <button className="close-btn" onClick={() => setShowCreateModal(false)}>×</button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label>Project Name *</label>
                <input
                  type="text"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  placeholder="My Awesome Project"
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label>Description (optional)</label>
                <textarea
                  value={newProjectDescription}
                  onChange={(e) => setNewProjectDescription(e.target.value)}
                  placeholder="What is this project about?"
                  rows={3}
                />
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="btn-secondary"
                onClick={() => setShowCreateModal(false)}
                disabled={loading}
              >
                Cancel
              </button>
              <button
                className="btn-primary"
                onClick={handleCreateProject}
                disabled={loading || !newProjectName.trim()}
              >
                {loading ? 'Creating...' : 'Create Project'}
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .beacon-project-button {
          position: fixed;
          top: 10px;
          left: 10px;
          z-index: 1000;
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          background: var(--vscode-button-background);
          color: var(--vscode-button-foreground);
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-family: var(--vscode-font-family);
        }

        .beacon-project-button:hover {
          background: var(--vscode-button-hoverBackground);
        }

        .project-icon {
          font-size: 16px;
        }

        .project-name {
          font-weight: 500;
          max-width: 200px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .dropdown-arrow {
          font-size: 10px;
          opacity: 0.7;
        }

        .beacon-project-switcher-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          z-index: 999;
          display: flex;
          align-items: flex-start;
          justify-content: flex-start;
          padding: 60px 20px;
        }

        .beacon-project-switcher {
          background: var(--vscode-editor-background);
          border: 1px solid var(--vscode-panel-border);
          border-radius: 8px;
          width: 400px;
          max-height: 600px;
          display: flex;
          flex-direction: column;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        .switcher-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          border-bottom: 1px solid var(--vscode-panel-border);
        }

        .switcher-header h2 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
        }

        .close-btn {
          background: none;
          border: none;
          color: var(--vscode-foreground);
          font-size: 24px;
          cursor: pointer;
          padding: 0;
          width: 30px;
          height: 30px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 4px;
        }

        .close-btn:hover {
          background: var(--vscode-toolbar-hoverBackground);
        }

        .workspace-selector {
          padding: 16px 20px;
          border-bottom: 1px solid var(--vscode-panel-border);
        }

        .workspace-selector label {
          display: block;
          margin-bottom: 8px;
          font-size: 12px;
          font-weight: 500;
          color: var(--vscode-descriptionForeground);
        }

        .workspace-selector select {
          width: 100%;
          padding: 8px;
          background: var(--vscode-input-background);
          color: var(--vscode-input-foreground);
          border: 1px solid var(--vscode-input-border);
          border-radius: 4px;
          font-family: var(--vscode-font-family);
          font-size: 14px;
        }

        .projects-list {
          flex: 1;
          overflow-y: auto;
          padding: 8px 0;
        }

        .project-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 20px;
          cursor: pointer;
          transition: background 0.2s;
        }

        .project-item:hover {
          background: var(--vscode-list-hoverBackground);
        }

        .project-item.active {
          background: var(--vscode-list-activeSelectionBackground);
          color: var(--vscode-list-activeSelectionForeground);
        }

        .project-info {
          flex: 1;
          min-width: 0;
        }

        .project-name {
          font-weight: 500;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .project-description {
          font-size: 12px;
          color: var(--vscode-descriptionForeground);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .empty-state {
          padding: 40px 20px;
          text-align: center;
          color: var(--vscode-descriptionForeground);
        }

        .empty-state button {
          margin-top: 16px;
          padding: 8px 16px;
          background: var(--vscode-button-background);
          color: var(--vscode-button-foreground);
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-family: var(--vscode-font-family);
        }

        .switcher-footer {
          padding: 12px 20px;
          border-top: 1px solid var(--vscode-panel-border);
        }

        .create-project-btn {
          width: 100%;
          padding: 10px;
          background: var(--vscode-button-secondaryBackground);
          color: var(--vscode-button-secondaryForeground);
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-family: var(--vscode-font-family);
          font-size: 14px;
        }

        .create-project-btn:hover {
          background: var(--vscode-button-secondaryHoverBackground);
        }

        /* Modal styles omitted for brevity - follow similar pattern */
      `}</style>
    </>
  );
};

export default ProjectSwitcher;

