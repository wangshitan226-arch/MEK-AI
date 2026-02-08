import React from 'react';
import { RouteObject } from 'react-router-dom';
import KnowledgeBaseBridge from './KnowledgeBaseBridge';

export const knowledgeBaseRoutes: RouteObject = {
  path: 'knowledge-base',
  element: <KnowledgeBaseBridge />,
};