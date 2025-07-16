export default {
  title: 'Knowledge',
  createDataset: 'Create Knowledge',
  general: 'General',
  web: 'Web Site',
  lark: 'Lark',
  relatedApplications: 'Linked App',
  document_count: 'docs',
  relatedApp_count: 'linked apps',
  searchBar: {
    placeholder: 'Search by name'
  },
  setting: {
    vectorization: 'Vectorization',
    sync: 'Sync'
  },
  tip: {
    professionalMessage:
      'The community edition supports up to 50 knowledge. For more knowledge, please upgrade to the professional edition.',
    syncSuccess: 'Sync task sent successfully',
    updateModeMessage:
      'After modifying the knowledge vector model, you need to vectorize the knowledge. Do you want to continue saving?'
  },
  delete: {
    confirmTitle: 'Confirm deletion of knowledge:',
    confirmMessage1: 'This knowledge is related with',
    confirmMessage2: 'APP. Deleting it will be irreversible, please proceed with caution.'
  },
  tabs: {
    myDataset: 'My Knowledge',
    sharedDataset: 'Shared Knowledge',
    organizationDataset: 'Organization Knowledge',
    sharedToMeDataset: 'Shared To Me',
    searchDataset: 'Knowledge Search',
    recycleBin: 'Recycle Bin'
  },
  searchDataset: {
    selectDatasets: 'Select Knowledge',
    selectDatasetsPlaceholder: 'Please add knowledge to search first',
    searchResult: 'Search Results',
    searchResultTip: 'Search content across multiple knowledge bases',
    emptyMessage1: 'Please enter content to start multi-knowledge search',
    emptyMessage2: 'No relevant content found',
    inputPlaceholder: 'Please enter the content you want to search',
    noDatasetSelected: 'Please select at least one knowledge base first'
  },
  datasetForm: {
    title: {
      info: 'Knowledge Settings'
    },
    form: {
      datasetName: {
        label: 'Name',
        placeholder: 'Please enter the knowledge name',
        requiredMessage: 'Please enter the knowledge name'
      },
      datasetDescription: {
        label: 'Description',
        placeholder:
          'Describe the content of the knowledge. A detailed description will help AI understand the content better, improving the accuracy of content retrieval and hit rate.',
        requiredMessage: 'Please enter the knowledge description'
      },
      EmbeddingModel: {
        label: 'Embedding Model',
        placeholder: 'Please select a embedding model',
        requiredMessage: 'Please select the embedding model'
      },
      datasetType: {
        label: 'Type',
        generalInfo: 'Upload local documents',
        webInfo: 'Sync text data from a web site',
        larkInfo: 'Sync documents from Feishu',
        yuqueInfo: 'Sync documents from Yuque'
      },
      source_url: {
        label: 'Web Root URL',
        placeholder: 'Please enter the web root URL',
        requiredMessage: 'Please enter the web root URL'
      },
      user_id: {
        requiredMessage: 'Please enter User ID'
      },
      token: {
        requiredMessage: 'Please enter Token'
      },
      selector: {
        label: 'Selector',
        placeholder: 'Default is body, can input .classname/#idname/tagname'
      }
    }
  },
  ResultSuccess: {
    title: 'Knowledge Created Successfully',
    paragraph: 'Segments',
    paragraph_count: 'Segments',
    documentList: 'Document List',
    loading: 'Importing',
    buttons: {
      toDataset: 'Return to Knowledge List',
      toDocument: 'Go to Document'
    }
  },
  syncWeb: {
    title: 'Sync Knowledge',
    syncMethod: 'Sync Method',
    replace: 'Replace Sync',
    replaceText: 'Re-fetch Web site documents, replacing the documents in the local knowledge',
    complete: 'Full Sync',
    completeText: 'Delete all documents in the local knowledge and re-fetch web site documents',
    tip: 'Note: All syncs will delete existing data and re-fetch new data. Please proceed with caution.'
  },
  addDataset: 'Add Knowledge',
  addDatasetPlaceholder: 'Please select knowledge to add',
  selected: 'Selected',
  countDataset: 'knowledge bases',
  recycleBin: {
    title: 'Recycle Bin',
    deleted: 'Deleted',
    restore: 'Restore',
    permanentlyDelete: 'Permanently Delete',
    emptyMessage: 'No deleted knowledge bases',
    developingMessage: 'Recycle Bin Feature Under Development',
    developingTip: 'This feature is currently under development, please stay tuned'
  },
  restore: {
    confirmTitle: 'Restore Knowledge',
    confirmMessage: 'Are you sure you want to restore this knowledge base?',
    success: 'Restore successful'
  },
  permanentlyDelete: {
    confirmTitle: 'Permanently Delete Knowledge',
    confirmMessage: 'Are you sure you want to permanently delete this knowledge base? This action cannot be undone.',
    success: 'Permanently delete successful'
  }
}
