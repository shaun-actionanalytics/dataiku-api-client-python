from .discussion import DSSObjectDiscussions

class DSSJupyterNotebook(object):
    def __init__(self, client, project_key, notebook_name):
       self.client = client
       self.project_key = project_key
       self.notebook_name = notebook_name

    def unload(self, session_id=None):
        """
        Stop this Jupyter notebook and release its resources
        """
        sessions = self.get_sessions()
        if sessions is None:
            raise Exception("Notebook isn't running")
        if len(sessions) == 0:
            raise Exception("Notebook isn't running")
        if session_id is None:
            if len(sessions) > 1:
                raise Exception("Several sessions of the notebook are running, choose one")
            else:
                session_id = sessions[0].get('sessionId', None)
        return self.client._perform_json("DELETE",
                                         "/projects/%s/jupyter-notebooks/%s/sessions/%s" % (self.project_key, self.notebook_name, session_id))

    def get_sessions(self, as_objects=False):
        """
        Get the list of running sessions of this Jupyter notebook

        :param boolean as_objects: if True, each returned item will be a :class:`dataikuapi.dss.notebook.DSSNotebookSession`
        :rtype: list of :class:`dataikuapi.dss.notebook.DSSNotebookSession` or list of dict
        """
        sessions = self.client._perform_json("GET",
                                             "/projects/%s/jupyter-notebooks/%s/sessions" % (self.project_key, self.notebook_name))

        if as_objects:
            return [DSSNotebookSession(self.client, session) for session in sessions]
        else:
            return sessions

    def get_contents(self):
        """
        Get the content of this Jupyter notebook (metadata, cells, nbformat)
        """
        raw_contents = self.client._perform_json("GET", "/projects/%s/jupyter-notebooks/%s" % (self.project_key, self.notebook_name))
        return DSSNotebookContents(self.client, self.project_key, self.notebook_name, raw_contents)

    def delete(self):
        """
        Delete this Jupyter notebook and stop all of its active sessions.
        """
        return self.client._perform_json("DELETE",
                                         "/projects/%s/jupyter-notebooks/%s" % (self.project_key, self.notebook_name))

    ########################################################
    # Discussions
    ########################################################
    def get_object_discussions(self):
        """
        Get a handle to manage discussions on the notebook

        :returns: the handle to manage discussions
        :rtype: :class:`dataikuapi.discussion.DSSObjectDiscussions`
        """
        return DSSObjectDiscussions(self.client, self.project_key, "JUPYTER_NOTEBOOK", self.notebook_name)

class DSSNotebookContents(object):
    """
    Contents of a Jupyter Notebook. Do not create this directly, use :meth:`DSSJupyterNotebook.get_contents`
    """

    """
    A Python/R/Scala notebook on the DSS instance
    """
    def __init__(self, client, project_key, notebook_name, contents):
        self.client = client
        self.project_key = project_key
        self.notebook_name = notebook_name
        self.contents = contents

    def get_raw(self):
        """
        Get the contents of this Jupyter notebook (metadata, cells, nbformat)
        :rtype: a dict containing the full contents of a notebook
        """
        return self.contents

    def get_metadata(self):
        """
        Get the metadata associated to this Jupyter notebook
        :rtype: dict with metadata
        """
        return self.contents["metadata"]

    def get_cells(self):
        """
        Get the cells associated to this Jupyter notebook
        :rtype: list of cells
        """
        return self.contents["cells"]

    def save(self):
        """
        Save the contents of this Jupyter notebook
        """
        return self.client._perform_json("PUT",
                                         "/projects/%s/jupyter-notebooks/%s" % (self.project_key, self.notebook_name),
                                         body=self.contents)

class DSSNotebookSession(object):
    """
    Metadata associated to the session of a Jupyter Notebook. Do not create this directly, use :meth:`DSSJupyterNotebook.get_sessions()`
    """

    def __init__(self, client, session):
        self.client = client
        self.project_key = session.get("projectKey")
        self.notebook_name = session.get("notebookName")
        self.session_creator = session.get("sessionCreator")
        self.session_creator_display_name = session.get("sessionCreatorDisplayName")
        self.session_unix_owner = session.get("sessionUnixOwner")
        self.session_id = session.get("sessionId")
        self.kernel_id = session.get("kernelId")
        self.kernel_pid = session.get("kernelPid")
        self.kernel_connections = session.get("kernelConnections")
        self.kernel_last_activity_time = session.get("kernelLastActivityTime")
        self.kernel_execution_state = session.get("kernelExecutionState")
        self.session_start_time = session.get("sessionStartTime")


    def unload(self):
        """
        Stop this Jupyter notebook and release its resources
        """
        return self.client._perform_json("DELETE",
                                         "/projects/%s/jupyter-notebooks/%s/sessions/%s" % (self.project_key, self.notebook_name, self.session_id))
